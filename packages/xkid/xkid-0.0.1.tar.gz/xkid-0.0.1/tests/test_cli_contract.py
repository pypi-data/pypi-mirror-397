from xkid.cli import contract


def test_cli_contract_constants():
    assert contract.COMMAND_RESULT_SCHEMA == "xkid.CommandResult.v1"

    assert contract.CMD_LENS_LIST == "lens.list"
    assert contract.CMD_LENS_DESCRIBE == "lens.describe"
    assert contract.CMD_ID_GENERATE == "id.generate"

    assert contract.DEFAULT_OUTPUT_FORMAT == "json"
    assert "raw" in contract.OUTPUT_FORMATS
