import json
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("ESCOPO_RESTLIB2", "test-scope")

from nsj_rest_lib2.compiler.compiler import EDLCompiler
from nsj_rest_lib2.compiler.edl_model.entity_model import EntityModel
from nsj_rest_lib2.compiler.edl_model.entity_model_root import EntityModelRoot
from nsj_rest_lib2.compiler.util.type_naming_util import (
    compile_function_class_name,
)
from nsj_rest_lib2.dto.escopo_dto import EscopoDTO


def _load_entity(path: Path):
    with path.open("r") as fp:
        edl_data = json.load(fp)

    model = (
        EntityModelRoot(**edl_data)
        if edl_data.get("mixin", False)
        else EntityModel(**edl_data)
    )
    complete_id = f"{model.escopo}/{model.id}"
    return complete_id, model


def _load_entity_models(base_dir: Path) -> dict[str, EntityModel]:
    models: dict[str, EntityModel] = {}
    for path in base_dir.iterdir():
        if path.suffix.lower() != ".json":
            continue
        key, model = _load_entity(path)
        models[key] = model
    return models


def test_compile_handlers_for_classificacao_financeira_generates_delete_function_type():
    base_dir = ROOT_DIR / "@schemas_test"
    entity_models = _load_entity_models(base_dir)

    model_key = "financas/ClassificacaoFinanceira"
    entity_model = entity_models[model_key]

    compiler = EDLCompiler()
    escopo = EscopoDTO(codigo=entity_model.escopo, service_account=None)
    result = compiler.compile_model(
        entity_model,
        list(entity_models.items()),
        escopo=escopo,
    )

    assert result is not None

    # Nomes das funções de banco para post/put/delete
    assert result.insert_function_name == "financas.api_classificacaofinanceiranovo"
    assert result.update_function_name == "financas.api_classificacaofinanceiraalterar"
    assert result.delete_function_name == "financas.api_classificacaofinanceiraexcluir"

    # FunctionType para delete
    delete_code = result.source_delete_function_type
    assert delete_code is not None

    expected_class = compile_function_class_name(entity_model.id, "", [], "delete")
    assert result.delete_function_type_class_name == expected_class
    assert f"class {expected_class}" in delete_code
    # Campos esperados (derivados do mapping do handler de delete)
    assert "classificacao: uuid.UUID = FunctionField(" in delete_code
    assert "grupoempresarial: uuid.UUID = FunctionField(" in delete_code


def test_compile_handlers_generates_get_and_list_function_types_from_edl():
    edl_json = {
        "edl_version": "1.0",
        "escopo": "test",
        "description": "Entidade de teste para funções GET/LIST.",
        "id": "Foo",
        "version": "1.0",
        "properties": {
            "id": {"type": "uuid", "pk": True},
            "codigo": {"type": "string"},
        },
        "repository": {
            "map": "test.foo",
            "shared_table": False,
            "properties": {
                "id": {"column": "id"},
                "codigo": {"column": "codigo"},
            },
            "indexes": [],
        },
        "api": {
            "resource": "foos",
            "expose": True,
            "verbs": ["GET"],
            "handlers": {
                "get": {
                    "impl": "pg_function",
                    "function_ref": "test.fn_foo_get",
                    "call": {
                        "arg_binding": {
                            "type_name": "test.tfoo_get",
                            "mapping": [
                                {"attr": "id_func", "from": "path.id"},
                                {"attr": "tenant", "from": "args.tenant"},
                            ],
                        }
                    },
                    "result": {"expected": "entity_row"},
                },
                "list": {
                    "impl": "pg_function",
                    "function_ref": "test.fn_foo_list",
                    "call": {
                        "arg_binding": {
                            "type_name": "test.tfoo_list",
                            "mapping": [
                                {"attr": "tenant", "from": "args.tenant"},
                                {"attr": "search", "from": "args.search"},
                            ],
                        }
                    },
                    "result": {"expected": "entity_row"},
                },
            },
        },
    }

    compiler = EDLCompiler()
    escopo = EscopoDTO(codigo="test", service_account=None)
    result = compiler.compile_model_from_edl(edl_json, [], escopo=escopo)

    assert result is not None
    assert result.get_function_name == "test.fn_foo_get"
    assert result.list_function_name == "test.fn_foo_list"

    get_code = result.source_get_function_type
    list_code = result.source_list_function_type
    assert get_code is not None
    assert list_code is not None

    expected_get_class = compile_function_class_name("Foo", "", [], "get")
    expected_list_class = compile_function_class_name("Foo", "", [], "list")

    assert result.get_function_type_class_name == expected_get_class
    assert result.list_function_type_class_name == expected_list_class
    assert f"class {expected_get_class}" in get_code
    assert "id_func: uuid.UUID = FunctionField(" in get_code
    assert "tenant: Any = FunctionField(" in get_code

    assert f"class {expected_list_class}" in list_code
    assert "tenant: Any = FunctionField(" in list_code
    assert "search: Any = FunctionField(" in list_code
