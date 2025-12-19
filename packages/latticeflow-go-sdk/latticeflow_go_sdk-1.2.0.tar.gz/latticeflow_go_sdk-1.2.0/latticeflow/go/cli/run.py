from __future__ import annotations

from pathlib import Path

import typer

import latticeflow.go.cli.utils.arguments as cli_args
import latticeflow.go.cli.utils.exceptions as cli_exc
import latticeflow.go.cli.utils.printing as cli_print
from latticeflow.go.cli.dataset_generators import (
    create_or_update_single_dataset_generator,
)
from latticeflow.go.cli.datasets import create_or_update_single_dataset
from latticeflow.go.cli.model_adapters import create_or_update_single_model_adapter
from latticeflow.go.cli.models import add_model_from_provider
from latticeflow.go.cli.models import map_and_add_single_custom_model
from latticeflow.go.cli.tasks import create_or_update_single_task
from latticeflow.go.cli.utils.dtypes import CLICreateEvaluation
from latticeflow.go.cli.utils.dtypes import CLICreateProviderAndModelKey
from latticeflow.go.cli.utils.dtypes import CLICreateRunConfig
from latticeflow.go.cli.utils.env_vars import get_cli_env_vars
from latticeflow.go.cli.utils.helpers import app_callback
from latticeflow.go.cli.utils.helpers import create_single_entity
from latticeflow.go.cli.utils.helpers import get_client_from_env
from latticeflow.go.cli.utils.helpers import load_ai_app_key
from latticeflow.go.cli.utils.printing import summarize_exception_chain
from latticeflow.go.cli.utils.schema_mappers import EntityByIdentifiersMap
from latticeflow.go.cli.utils.schema_mappers import map_dataset_cli_to_api_entity
from latticeflow.go.cli.utils.schema_mappers import (
    map_dataset_generator_cli_to_api_entity,
)
from latticeflow.go.cli.utils.schema_mappers import map_evaluation_cli_to_api_entity
from latticeflow.go.cli.utils.schema_mappers import map_model_adapter_cli_to_api_entity
from latticeflow.go.cli.utils.schema_mappers import map_task_cli_to_api_entity
from latticeflow.go.cli.utils.single_commands import with_callback
from latticeflow.go.cli.utils.yaml_utils import load_yaml_recursively
from latticeflow.go.client import Client
from latticeflow.go.models import EvaluationAction
from latticeflow.go.models import StoredAIApp
from latticeflow.go.models import StoredEvaluation


def register_run_command(app: typer.Typer) -> None:
    app.command(
        name="run",
        short_help="Create and run an evaluation and its dependencies from a run config file.",
        help=(
            "Create and run an evaluation along with its dependencies (models, model adapters, "
            "dataset generators, datasets, and tasks) as specified in a run config YAML file. "
            "You can optionally validate the configuration."
        ),
    )(with_callback(lambda: app_callback(get_cli_env_vars))(_run))


def _run(
    path: Path = cli_args.single_config_path_argument("run config"),
    should_validate_only: bool = cli_args.should_validate_only_option,
) -> None:
    """Create and run an evaluation along with its dependencies from a run config file."""
    ai_app_key = load_ai_app_key()
    client = get_client_from_env()

    if should_validate_only:
        _validate_run_config(path)
        return

    stored_ai_app = client.ai_apps.get_ai_app_by_key(ai_app_key)
    run_config = _get_cli_run_config_from_file(path)

    added_model_adapters = _process_model_adapters(run_config, path, client)
    added_models = _process_models(run_config, path, client)
    added_dataset_generators = _process_dataset_generators(run_config, path, client)
    added_datasets = _process_datasets(run_config, path, client)
    added_tasks = _process_tasks(run_config, path, client)

    added_evaluations = 0
    if run_config.evaluation is not None:
        cli_print.log_info(
            f"Creating and running an evaluation defined in the config at path '{path}'."
        )
        try:
            stored_evaluation = _create_evaluation(
                client, run_config.evaluation, stored_ai_app, path
            )
        except Exception as error:
            cli_print.log_error(
                f"Could not create/update evaluation from config at path '{path}':"
                f"\n{summarize_exception_chain(error)}"
            )

        try:
            _run_evaluation(client, stored_evaluation, stored_ai_app)
            added_evaluations = 1
        except Exception as error:
            cli_print.log_error(
                f"Could not start evaluation with ID '{stored_evaluation.id}':"
                f"\n{summarize_exception_chain(error)}"
            )

    total_entities_to_be_added = (
        len(run_config.model_adapters)
        + len(run_config.models)
        + len(run_config.dataset_generators)
        + len(run_config.datasets)
        + len(run_config.tasks)
        + (1 if run_config.evaluation is not None else 0)
    )
    total_added_entities = (
        added_model_adapters
        + added_models
        + added_dataset_generators
        + added_datasets
        + added_tasks
        + added_evaluations
    )
    if total_added_entities < total_entities_to_be_added:
        raise typer.Exit(code=1)


def _get_cli_run_config_from_file(config_file: Path) -> CLICreateRunConfig:
    try:
        return CLICreateRunConfig.model_validate(
            load_yaml_recursively(config_file), ignore_extra=False
        )
    except Exception as error:
        raise cli_exc.CLIInvalidConfigError("run config", config_file, None) from error


def _validate_run_config(config_file: Path) -> None:
    try:
        _get_cli_run_config_from_file(config_file)
        cli_print.log_validation_success_info(config_file)
    except Exception as error:
        cli_print.log_validation_fail_error(config_file, error)
        raise cli_exc.CLIValidationError("run config") from error


def _process_model_adapters(
    run_config: CLICreateRunConfig, config_file: Path, client: Client
) -> int:
    added = 0
    if len(run_config.model_adapters) > 0:
        cli_print.log_creating_or_updating_entities_info("model adapters", config_file)
        model_adapters_map = EntityByIdentifiersMap(
            client.model_adapters.get_model_adapters().model_adapters
        )
        for cli_model_adapter in run_config.model_adapters:
            try:
                model_adapter = map_model_adapter_cli_to_api_entity(
                    cli_model_adapter=cli_model_adapter, config_file=config_file
                )
                stored_model_adapter = model_adapters_map.get_entity_by_key(
                    cli_model_adapter.key
                )
                new_stored_model_adapter = create_or_update_single_model_adapter(
                    client, model_adapter, stored_model_adapter
                )
                added += 1
                model_adapters_map.update_entity(new_stored_model_adapter)
            except Exception as error:
                cli_print.log_create_update_fail_error(
                    "model adapter", config_file, error
                )
        cli_print.log_char_full_width("─")
    return added


def _process_models(
    run_config: CLICreateRunConfig, config_file: Path, client: Client
) -> int:
    added = 0
    if len(run_config.models) > 0:
        cli_print.log_creating_or_updating_entities_info("models", config_file)
        models_map = EntityByIdentifiersMap(client.models.get_models().models)
        model_adapters_map = EntityByIdentifiersMap(
            client.model_adapters.get_model_adapters().model_adapters
        )
        for cli_model in run_config.models:
            try:
                if isinstance(cli_model, CLICreateProviderAndModelKey):
                    new_stored_model = add_model_from_provider(
                        cli_model.provider_and_model_key, models_map, client
                    )
                else:
                    new_stored_model = map_and_add_single_custom_model(
                        client=client,
                        cli_model=cli_model,
                        model_adapters_map=model_adapters_map,
                        models_map=models_map,
                        config_file=config_file,
                    )
                models_map.update_entity(new_stored_model)
                added += 1
            except Exception as error:
                cli_print.log_create_update_fail_error("model", config_file, error)
        cli_print.log_char_full_width("─")
    return added


def _process_dataset_generators(
    run_config: CLICreateRunConfig, config_file: Path, client: Client
) -> int:
    added = 0
    if len(run_config.dataset_generators) > 0:
        cli_print.log_creating_or_updating_entities_info(
            "dataset generators", config_file
        )
        dataset_generators_map = EntityByIdentifiersMap(
            client.dataset_generators.get_dataset_generators().dataset_generators
        )
        datasets_map = EntityByIdentifiersMap(client.datasets.get_datasets().datasets)
        models_map = EntityByIdentifiersMap(client.models.get_models().models)
        for cli_dataset_generator in run_config.dataset_generators:
            try:
                dataset_generator = map_dataset_generator_cli_to_api_entity(
                    cli_dataset_generator=cli_dataset_generator,
                    datasets_map=datasets_map,
                    models_map=models_map,
                    config_file=config_file,
                )
                stored_dataset_generator = dataset_generators_map.get_entity_by_key(
                    dataset_generator.key
                )
                new_stored_dataset_generator = (
                    create_or_update_single_dataset_generator(
                        client, dataset_generator, stored_dataset_generator
                    )
                )
                added += 1
                dataset_generators_map.update_entity(new_stored_dataset_generator)
            except Exception as error:
                cli_print.log_create_update_fail_error(
                    "dataset generator", config_file, error
                )
        cli_print.log_char_full_width("─")
    return added


def _process_datasets(
    run_config: CLICreateRunConfig, config_file: Path, client: Client
) -> int:
    added = 0
    if len(run_config.datasets) > 0:
        cli_print.log_creating_or_updating_entities_info("datasets", config_file)
        models_map = EntityByIdentifiersMap(client.models.get_models().models)
        datasets_map = EntityByIdentifiersMap(client.datasets.get_datasets().datasets)
        dataset_generators_map = EntityByIdentifiersMap(
            client.dataset_generators.get_dataset_generators().dataset_generators
        )
        for cli_dataset in run_config.datasets:
            try:
                (dataset, dataset_file_path, dataset_generation_request_with_id) = (
                    map_dataset_cli_to_api_entity(
                        cli_dataset=cli_dataset,
                        models_map=models_map,
                        datasets_map=datasets_map,
                        dataset_generators_map=dataset_generators_map,
                        config_file=config_file,
                    )
                )
                stored_dataset = datasets_map.get_entity_by_key(cli_dataset.key)
                new_stored_dataset = create_or_update_single_dataset(
                    client,
                    dataset,
                    dataset_file_path,
                    dataset_generation_request_with_id,
                    stored_dataset,
                    config_file,
                )
                added += 1
                datasets_map.update_entity(new_stored_dataset)
            except Exception as error:
                cli_print.log_create_update_fail_error("dataset", config_file, error)
        cli_print.log_char_full_width("─")
    return added


def _process_tasks(
    run_config: CLICreateRunConfig, config_file: Path, client: Client
) -> int:
    added = 0
    if len(run_config.tasks) > 0:
        cli_print.log_creating_or_updating_entities_info("tasks", config_file)
        tasks_map = EntityByIdentifiersMap(client.tasks.get_tasks().tasks)
        models_map = EntityByIdentifiersMap(client.models.get_models().models)
        datasets_map = EntityByIdentifiersMap(client.datasets.get_datasets().datasets)
        for cli_task in run_config.tasks:
            try:
                task = map_task_cli_to_api_entity(
                    cli_task=cli_task,
                    models_map=models_map,
                    datasets_map=datasets_map,
                    config_file=config_file,
                )
                stored_task = tasks_map.get_entity_by_key(task.key)
                new_stored_task = create_or_update_single_task(
                    client, task, stored_task
                )
                added += 1
                tasks_map.update_entity(new_stored_task)
            except Exception as error:
                cli_print.log_create_update_fail_error("task", config_file, error)
        cli_print.log_char_full_width("─")
    return added


def _create_evaluation(
    client: Client,
    cli_evaluation: CLICreateEvaluation,
    stored_ai_app: StoredAIApp,
    config_file: Path,
) -> StoredEvaluation:
    evaluation = map_evaluation_cli_to_api_entity(
        cli_evaluation=cli_evaluation,
        models_map=EntityByIdentifiersMap(client.models.get_models().models),
        datasets_map=EntityByIdentifiersMap(client.datasets.get_datasets().datasets),
        tasks_map=EntityByIdentifiersMap(client.tasks.get_tasks().tasks),
        config_file=config_file,
    )
    return create_single_entity(
        "evaluation",
        lambda: client.evaluations.create_evaluation(stored_ai_app.id, evaluation),
        None,
        None,
    )


def _run_evaluation(
    client: Client, stored_evaluation: StoredEvaluation, stored_ai_app: StoredAIApp
) -> None:
    client.evaluations.execute_action_evaluation(
        stored_ai_app.id, stored_evaluation.id, action=EvaluationAction.START
    )
    cli_print.log_info(
        f"Successfully started evaluation with ID '{stored_evaluation.id}'."
    )
