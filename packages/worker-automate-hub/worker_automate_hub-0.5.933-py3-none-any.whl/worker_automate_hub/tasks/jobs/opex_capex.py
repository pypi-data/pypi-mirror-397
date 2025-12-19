import difflib
import getpass
import os
import re
import warnings
import time
import uuid
from datetime import datetime, timedelta
import pyautogui
import pytesseract
import win32clipboard
from PIL import Image, ImageEnhance
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from pywinauto.timings import TimeoutError as PywTimeout, wait_until
from pywinauto_recorder.player import set_combobox
from rich.console import Console
import sys
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..","..")))
from worker_automate_hub.api.ahead_service import save_xml_to_downloads
from worker_automate_hub.api.client import (
    get_config_by_name,
    get_status_nf_emsys,
    get_dados_nf_emsys,
)
from worker_automate_hub.models.dto.rpa_historico_request_dto import (
    RpaHistoricoStatusEnum,
    RpaRetornoProcessoDTO,
    RpaTagDTO,
    RpaTagEnum,
)
from worker_automate_hub.models.dto.rpa_processo_entrada_dto import (
    RpaProcessoEntradaDTO,
)
from worker_automate_hub.utils.logger import logger
from worker_automate_hub.utils.util import (
    cod_icms,
    delete_xml,
    error_after_xml_imported,
    get_xml,
    import_nfe,
    incluir_registro,
    is_window_open,
    is_window_open_by_class,
    itens_not_found_supplier,
    kill_all_emsys,
    login_emsys,
    rateio_despesa,
    select_documento_type,
    set_variable,
    tipo_despesa,
    type_text_into_field,
    warnings_after_xml_imported,
    worker_sleep,
    zerar_icms,
    check_nota_importada,
)

pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = False
console = Console()


ASSETS_PATH = "assets"

async def rateio_despesa_centro_custo(centro_custo : str) -> RpaRetornoProcessoDTO:
    console.print(
        f"Conectando a tela de Rateio da Despesa para encerramento do processo...\n"
    )
    console.print(f"Código filial {centro_custo }...\n")
    try:

        console.print(f"Tentando clicar em Selecionar todos...\n")
        try:
            selecionar_todos = pyautogui.locateOnScreen(
                ASSETS_PATH + "\\entrada_notas\\SelecionarTodos.png", confidence=0.5
            )
            if selecionar_todos:
                console.print(f"Campo selecionar todos encontrado, interagindo...\n")
                pyautogui.click(selecionar_todos)

        except Exception as e:
            console.print(f"Error ao interagir com o campo de selecionar todos : {e}")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=f"Error ao interagir com o campo de selecionar todos : {e}",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)],
            )

        await worker_sleep(5)

        try:
            app = Application().connect(class_name="TFrmDadosRateioDespesa")
            main_window = app["TFrmDadosRateioDespesa"]
            console.print(f"Conectado com pela classe do emsys...\n")
        except:
            app = Application().connect(title="Rateio da Despesa")
            main_window = app["Rateio da Despesa"]
            console.print(f"Conectado pelo title...\n")

        main_window.set_focus()

        console.print(
            f"Conectado com sucesso, acessando o atributo filho 'Centro'...\n"
        )
        panel_centro = main_window.child_window(class_name="TPanel", found_index=1)

        console.print(
            f"Conectado com sucesso, inserindo o valor do tipo de despesa...\n"
        )

        edit = panel_centro.child_window(class_name="TDBIEditCode", found_index=1)

        try:
            value_centro = int(centro_custo)
        except ValueError:
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=f"Unidade code não é um número válido.",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)],
            )

        value_centro_str = str(value_centro)
        console.print(f"Valor final a ser inserido no Centro {value_centro_str}...\n")

        if edit.exists():
            edit.set_edit_text(value_centro_str)
            edit.type_keys("{TAB}")
        else:
            console.print(f"Campo tipo de despesas - Não foi encontrado...\n")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=f"Campo tipo de despesas - Não foi encontrado",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)],
            )

        console.print(f"Conectado com sucesso, inserindo o valor do rateio...\n")
        edit = panel_centro.child_window(class_name="TDBIEditNumber", found_index=0)

        if edit.exists():
            edit.set_edit_text("100")
            edit.click()
            edit.type_keys("{TAB}")
        else:
            console.print(f"Campo valor do rateio - Não foi encontrado...\n")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=f"Campo valor do rateio - Não foi encontrado",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)],
            )

        await worker_sleep(3)

        console.print(
            f"Selecionando a opção 'Aplicar Rateio aos Itens Selecionados'...\n"
        )
        try:
            checkbox = panel_centro.child_window(
                title="Aplicar Rateio aos Itens Selecionados",
                class_name="TDBICheckBox",
            )
            checkbox.click()
            console.print(
                "A opção 'Aplicar Rateio aos Itens Selecionados' selecionado com sucesso... \n"
            )
        except:
            try:
                aplicar_rateio = pyautogui.locateOnScreen(
                    ASSETS_PATH + "\\entrada_notas\\aplicar_rateio_itens.png",
                    confidence=0.5,
                )
                if aplicar_rateio:
                    console.print(
                        f"Campo aplicar rateio itens encontrado, clicando...\n"
                    )
                    center_x, center_y = pyautogui.center(aplicar_rateio)
                    try:
                        pyautogui.click(center_x, center_y)
                    except:
                        pyautogui.click(aplicar_rateio)
            except:
                try:
                    app = Application().connect(title="Busca Centro de Custo")
                    main_window = app["Busca Centro de Custo"]
                    return RpaRetornoProcessoDTO(
                        sucesso=False,
                        retorno=f"Centro de custo não localizado na tela de rateio, por favor, verificar",
                        status=RpaHistoricoStatusEnum.Falha,
                        tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)],
                    )
                except Exception as e:
                    return RpaRetornoProcessoDTO(
                        sucesso=False,
                        retorno=f"Campo aplicar rateio - Não foi encontrado, erro: {e}",
                        status=RpaHistoricoStatusEnum.Falha,
                        tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)],
                    )

        console.print(f"Tentando clicar em Incluir Registro...\n")
        await worker_sleep(2)
        try:
            console.print(
                f"Não foi possivel clicar em Incluir Registro, tentando via hotkeys..\n"
            )
            pyautogui.press("tab")
            pyautogui.press("tab")
            await worker_sleep(2)
            pyautogui.press("enter")
            await worker_sleep(4)
        except Exception as e:
            try:
                incluir_registro_rateio = pyautogui.locateOnScreen(
                    ASSETS_PATH
                    + "\\entrada_notas\\importar_registro_rateio_despesas.png",
                    confidence=0.5,
                )
                if incluir_registro_rateio:
                    console.print(
                        f"Campo selecionar todos encontrado, interagindo...\n"
                    )
                    pyautogui.click(incluir_registro_rateio)
            except:
                console.print(
                    f"Clicando em Incluir registro para vincular ao centro de custo '...\n"
                )
                edit = panel_centro.child_window(
                    class_name="TDBITBitBtn", found_index=3
                )

                if edit.exists():
                    edit.click()
                else:
                    console.print(f"Campo Incluir registro nao foi encontrado...\n")
                    return RpaRetornoProcessoDTO(
                        sucesso=False,
                        retorno="Campo Incluir registro nao foi encontrado",
                        status=RpaHistoricoStatusEnum.Falha,
                        tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)],
                    )


        await worker_sleep(3)

        console.print(f"Verificando se o item foi rateado com sucesso...\n")
        panel_centro = main_window.child_window(class_name="TPanel", found_index=0)
        edit = panel_centro.child_window(class_name="TDBIEditNumber", found_index=0)

        if edit.exists():
            valor_total_rateado = edit.window_text()
            if valor_total_rateado != "0,00":
                console.print(f"Rateio inserido com sucesso., clicando em OK..\n")
                send_keys("%o")
                return RpaRetornoProcessoDTO(
                    sucesso=True,
                    retorno="Rateio de despesa interagido com sucesso",
                    status=RpaHistoricoStatusEnum.Sucesso,
                )

        else:
            console.print(f"Campo valor do rateio - Não foi encontrado...\n")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno="Campo valor do rateio - Não foi encontrado",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)],
            )

    except Exception as e:
        return RpaRetornoProcessoDTO(
            sucesso=False,
            retorno=f"Erro ao processar tela de Informações para importação da Nota Fiscal Eletrônica para inserir o tipo de despesa, erro: {e}",
            status=RpaHistoricoStatusEnum.Falha,
            tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)],
        )

async def get_ultimo_item():
    console.print("[ITENS] Iniciando função get_ultimo_item...", style="bold cyan")
    send_keys("^({END})")
    await worker_sleep(2)
    send_keys("+{F10}")
    await worker_sleep(1)
    send_keys("{DOWN 2}")
    await worker_sleep(1)
    send_keys("{ENTER}")
    await worker_sleep(2)
    console.print("[ITENS] Conectando na janela 'Alteração de Item' para obter último índice...", style="cyan")
    app = Application().connect(title="Alteração de Item")
    main_window = app["Alteração de Item"]
    main_window.set_focus()
    edit = main_window.child_window(class_name="TDBIEditCode", found_index=0)
    index_ultimo_item = int(edit.window_text())
    console.print(f"[ITENS] Último item encontrado: {index_ultimo_item}", style="bold green")
    try:
        btn_cancelar = main_window.child_window(title="&Cancelar")
        btn_cancelar.click()
    except Exception as error:
        btn_cancelar = main_window.child_window(title="Cancelar")
        btn_cancelar.click()
        console.print(f"[ITENS] Erro ao fechar janela get_ultimo_item: {error}", style="bold yellow")
    await worker_sleep(1)
    return index_ultimo_item   

 


async def opex_capex(task: RpaProcessoEntradaDTO) -> RpaRetornoProcessoDTO:
    numero_nota = None
    try:
        console.print("\n================ INÍCIO PROCESSO opex_capex ================\n", style="bold blue")
        console.print(f"[TASK] Dados da task recebida: {task}", style="cyan")

        console.print("[ETAPA 1] Buscando configuração de login_emsys via API...", style="bold cyan")
        config = await get_config_by_name("login_emsys")
        console.print("[ETAPA 1] Configuração 'login_emsys' obtida com sucesso.", style="bold green")

        nota = task.configEntrada
        console.print(f"[ETAPA 1] ConfigEntrada (nota): {nota}", style="cyan")

        multiplicador_timeout = int(float(task.sistemas[0].timeout))
        console.print(f"[ETAPA 1] Timeout multiplicador definido como: {multiplicador_timeout}", style="cyan")
        set_variable("timeout_multiplicador", multiplicador_timeout)

        console.print("[ETAPA 2] Fechando instâncias do EMSys se existirem...", style="bold cyan")
        await kill_all_emsys()
        data_atual = datetime.now().strftime("%d/%m/%Y")
        print(data_atual)       
       # Buscar número da nota
        numero_nota = nota.get("numeroNota")
        serie_nota = nota.get("serieNota")
        filial_nota = nota.get("descricaoFilial")
        filial_nota = filial_nota.split("-")[0].strip()

        centro_custo = nota.get("centroCusto")
        centro_custo = centro_custo.split("-")[0].strip().lstrip("0")

        # >>> AJUSTE IMPORTANTE <<<
        fornecedor_cnpj = nota.get("fornecedorCnpj")

        if not fornecedor_cnpj:
            raise ValueError("fornecedorCnpj não informado na entrada do processo")

        try:
            console.print(
                f"Buscando NF | Numero: {numero_nota} | Serie: {serie_nota} | "
                f"Filial: {filial_nota} | Fornecedor CNPJ: {fornecedor_cnpj}"
            )

            dados_nf = await get_dados_nf_emsys(
            numero_nota=numero_nota,
            serie_nota=serie_nota,
            filial_nota=filial_nota,
            fornecedor_cnpj=fornecedor_cnpj
            )
            console.print(f"[ETAPA 4] Retorno get_dados_nf_emsys: {dados_nf}", style="cyan")


            # Se a API retornou erro
            if isinstance(dados_nf, dict) and "erro" in dados_nf:
                console.print("[ETAPA 4] Erro retornado pela API de dados NF.", style="bold red")
                console.print(f"[ETAPA 4] Detalhes erro API: {dados_nf['erro']}", style="red")
                nf_chave_acesso = None
            elif isinstance(dados_nf, list) and not dados_nf:
                console.print("[ETAPA 4] Nenhum dado encontrado para a nota na API.", style="bold yellow")
                nf_chave_acesso = None
            else:
                nf_chave_acesso = dados_nf[0].get("chaveNfe")
                console.print(f"[ETAPA 4] Chave da NF obtida: {nf_chave_acesso}", style="bold green")

        except Exception as e:
            observacao = f"[ERRO ETAPA 4] Erro ao buscar nota via get_dados_nf_emsys: {e}"
            console.print(observacao, style="bold red")
            logger.error(observacao)
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=observacao,
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
            )

        console.print("[ETAPA 5] Iniciando download do XML da NF...", style="bold cyan")
        await save_xml_to_downloads(nf_chave_acesso)
        console.print("[ETAPA 5] XML baixado com sucesso.", style="bold green")

        console.print("[ETAPA 6] Consultando status da NF no EMSys via get_status_nf_emsys...", style="bold cyan")
        status_nf_emsys = await get_status_nf_emsys(nf_chave_acesso)
        console.print(f"[ETAPA 6] Status NF EMSys: {status_nf_emsys}", style="cyan")

        empresa_codigo = dados_nf[0]["empresaCodigo"]
        cfop = dados_nf[0]["numeroDoCfop"]
        cfops_itens = [item["cfopProduto"] for item in dados_nf[0]["itens"]]
        console.print(f"[ETAPA 6] EmpresaCodigo={empresa_codigo} | CFOP NF={cfop} | CFOPs Itens={cfops_itens}", style="cyan")

        if status_nf_emsys.get("status") == "Lançada":
            console.print("\\Nota fiscal já lançada, processo finalizado...", style="bold green")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno="Nota fiscal já lançada",
                status=RpaHistoricoStatusEnum.Descartado,
            )
        else:
            console.print("\\Nota fiscal não lançada, iniciando o processo...", style="yellow")
        
        console.print("[ETAPA 7] Iniciando EMSys3_29.exe...", style="bold cyan")
        app = Application(backend="win32").start("C:\\Rezende\\EMSys3\\EMSys3_29.exe")
        warnings.filterwarnings(
            "ignore",
            category=UserWarning,
            message="32-bit application should be automated usando 32-bit Python",
        )
        console.print("[ETAPA 7] EMSys iniciando...", style="bold green")

        console.print("[ETAPA 7] Realizando login no EMSys pelo login_emsys...", style="bold cyan")
        return_login = await login_emsys(config.conConfiguracao, app, task, filial_origem=empresa_codigo)

        if return_login.sucesso:
            console.print("[ETAPA 8] Login realizado com sucesso. Acessando menu 'Nota Fiscal de Entrada'...", style="bold green")
            type_text_into_field(
                "Nota Fiscal de Entrada", app["TFrmMenuPrincipal"]["Edit"], True, "50"
            )
            pyautogui.press("enter")
            await worker_sleep(2)
            pyautogui.press("enter")
            console.print("[ETAPA 8] Pesquisa: 'Nota Fiscal de Entrada' realizada com sucesso", style="bold green")
        else:
            logger.info(f"[ETAPA 8] Error Message login: {return_login.retorno}")
            console.print(f"[ETAPA 8] Error Message login: {return_login.retorno}", style="bold red")
            return return_login

        await worker_sleep(6)

        console.print("[ETAPA 9] Selecionando tipo de documento: NOTA FISCAL DE ENTRADA ELETRONICA - DANFE...", style="bold cyan")
        document_type = await select_documento_type(
            "NOTA FISCAL DE ENTRADA ELETRONICA - DANFE"
        )
        if document_type.sucesso:
            console.log(document_type.retorno, style="bold green")
        else:
            console.print("[ETAPA 9] Falha ao selecionar tipo de documento.", style="bold red")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=document_type.retorno,
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )

        await worker_sleep(4)

        console.print("[ETAPA 10] Iniciando importação da NFe (XML)...", style="bold cyan")
        imported_nfe = await import_nfe()
        if imported_nfe.sucesso:
            console.log(imported_nfe.retorno, style="bold green")
        else:
            console.print("[ETAPA 10] Falha na importação da NFe.", style="bold red")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=imported_nfe.retorno,
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )

        await worker_sleep(5)

        console.print("[ETAPA 11] Buscando XML importado no EMSys via get_xml...", style="bold cyan")
        await get_xml(nf_chave_acesso)
        console.print("[ETAPA 11] get_xml concluído.", style="bold green")
        
        await worker_sleep(10)

        console.print("[ETAPA 12] Verificando existência de pop-up 'Warning' após importação do XML...", style="bold cyan")
        warning_pop_up = await is_window_open("Warning")
        if warning_pop_up["IsOpened"]:
            console.print("[ETAPA 12] Pop-up Warning encontrado, tratando via warnings_after_xml_imported...", style="yellow")
            warning_work = await warnings_after_xml_imported()
            if warning_work.sucesso:
                console.log(warning_work.retorno, style="bold green")
            else:
                console.print("[ETAPA 12] Falha ao tratar Warning após XML.", style="bold red")
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=warning_work.retorno,
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                )

        console.print("[ETAPA 13] Verificando existência de pop-up 'Erro' após importação do XML...", style="bold cyan")
        erro_pop_up = await is_window_open("Erro")
        if erro_pop_up["IsOpened"]:
            console.print("[ETAPA 13] Pop-up Erro encontrado, tratando via error_after_xml_imported...", style="bold red")
            error_work = await error_after_xml_imported()
            return RpaRetornoProcessoDTO(
                sucesso=error_work.sucesso,
                retorno=error_work.retorno,
                status=error_work.status,
                tags=error_work.tags
            )
        
        await worker_sleep(3)

        console.print("[ETAPA 14] Conectando na janela 'Informações para importação da Nota Fiscal Eletrônica'...", style="bold cyan")
        app = Application().connect(title="Informações para importação da Nota Fiscal Eletrônica")
        main_window = app["Informações para importação da Nota Fiscal Eletrônica"]

        # ================= BLOCO CFOP =================
        console.print(f"[CFOP] Iniciando processo de seleção da Natureza de Operação (CFOP: {cfop})...", style="bold cyan")

        cfop_map = {
            "1556": (['5101', '5102', '5103', '5104'], "1.556"),
            "1407": (['5401', '5403', '5404', '5405'], "1.407"),
            "2407": (['6104', '6401', '6403', '6405'], "2.407")
        }

        cfop_str = str(cfop)
        cfop_key_escolhido = None
        codigo_combo_escolhido = None

        for key, (lista, codigo_combo) in cfop_map.items():
            if cfop_str in lista:
                cfop_key_escolhido = key
                codigo_combo_escolhido = codigo_combo
                break

        console.print(f"[CFOP] CFOP NF: {cfop_str} | CFOP key escolhida: {cfop_key_escolhido} | Código combo: {codigo_combo_escolhido}", style="cyan")

        if not cfop_key_escolhido:
            msg = "Erro mapeado, CFOP diferente de início com 540 ou 510, necessário ação manual ou ajuste no robô..."
            console.print(f"[CFOP] {msg}", style="bold red")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=msg,
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
            )

        max_tentativas_cfop = 3
        selecionou_cfop = False

        for tentativa in range(1, max_tentativas_cfop + 1):
            try:
                console.print(f"[CFOP] Tentando selecionar Natureza de Operação (tentativa {tentativa}/{max_tentativas_cfop})...", style="bold cyan")

                combo_box_natureza_operacao = main_window.child_window(
                    class_name="TDBIComboBox", found_index=0
                )

                combo_box_natureza_operacao.set_focus()
                combo_box_natureza_operacao.click_input()
                await worker_sleep(1)

                texto_alvo_parcial = f"{cfop_key_escolhido}-COMPRA DE MERCADORIAS SEM ESTOQUE"
                texto_alvo_codigo = str(codigo_combo_escolhido)

                console.print(f"[CFOP] Buscando opção que contenha '{texto_alvo_parcial}' e '{texto_alvo_codigo}'...", style="cyan")

                for opc in combo_box_natureza_operacao.item_texts():
                    if (texto_alvo_parcial in opc) and (texto_alvo_codigo in opc):
                        console.print(f"[CFOP] Opção candidata encontrada: {opc}", style="cyan")
                        combo_box_natureza_operacao.select(opc)
                        send_keys("{ENTER}")
                        await worker_sleep(1)

                        texto_final = combo_box_natureza_operacao.window_text().strip()
                        console.print(f"[CFOP] Texto final no combo: '{texto_final}'", style="cyan")
                        if texto_alvo_codigo in texto_final or cfop_key_escolhido in texto_final:
                            selecionou_cfop = True
                            console.print(f"[CFOP] Natureza de Operação selecionada com sucesso: {texto_final}", style="bold green")
                            break

                if selecionou_cfop:
                    break
                else:
                    console.print("[CFOP] Não foi possível confirmar a seleção da Natureza de Operação. Tentando novamente...", style="yellow")
                    await worker_sleep(2)

            except Exception as e:
                console.print(f"[CFOP] Erro ao selecionar Natureza de Operação na tentativa {tentativa}: {e}", style="bold red")
                await worker_sleep(2)

        if not selecionou_cfop:
            msg = "Não foi possível selecionar a Natureza de Operação (CFOP) após múltiplas tentativas."
            console.print(f"[CFOP] {msg}", style="bold red")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=msg,
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )

        console.print(f"[CFOP] CFOP selecionado com base em {cfop_key_escolhido}. CFOP original da NF: {cfop}", style="bold green")

        await worker_sleep(3)

        # ================= ALMOXARIFADO =================
        console.print("[ALMOXARIFADO] Iniciando preenchimento do almoxarifado...", style="bold cyan")
        fornecedor_nome = dados_nf[0]["fornecedorNome"]
        empresaCodigo = dados_nf[0]["empresaCodigo"]
        console.print(f"[ALMOXARIFADO] Fornecedor: {fornecedor_nome} | EmpresaCodigo: {empresaCodigo}", style="cyan")
        console.print(f"[ALMOXARIFADO] Inserindo informação do Almoxarifado para empresa_codigo={empresa_codigo}...", style="cyan")
        try:
            new_app = Application(backend="uia").connect(title="Informações para importação da Nota Fiscal Eletrônica")
            window = new_app["Informações para importação da Nota Fiscal Eletrônica"]
            edit = window.child_window(class_name="TDBIEditCode", found_index=3, control_type="Edit")
            if empresa_codigo == '1':
                valor_almoxarifado = empresaCodigo + "60"
            else:
                valor_almoxarifado = empresaCodigo + "50"
            console.print(f"[ALMOXARIFADO] Valor a ser inserido no almoxarifado: {valor_almoxarifado}", style="cyan")
            edit.set_edit_text(valor_almoxarifado)
            edit.type_keys("{TAB}")
            console.print("[ALMOXARIFADO] Almoxarifado preenchido com sucesso.", style="bold green")
        except Exception as e:
            console.print(f"[ALMOXARIFADO] Erro ao iterar itens de almoxarifado: {e}", style="bold red")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=f"Erro ao iterar itens de almoxarifado: {e}",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )

        await worker_sleep(3)

        # ================= DESPESA =================
        console.print("[DESPESA] Inserindo conta contábil / tipo de despesa...", style="bold cyan")
        despesa = nota.get('contaContabil')
        console.print(f"[DESPESA] Conta contábil original: {despesa}", style="cyan")
        despesa = despesa.split("-")[0].strip()
        console.print(f"[DESPESA] Conta contábil tratada (apenas código): {despesa}", style="cyan")
        tipo_despesa_work = await tipo_despesa(despesa)
        if tipo_despesa_work.sucesso:
            console.log(tipo_despesa_work.retorno, style="bold green")
        else:
            console.print("[DESPESA] Falha na função tipo_despesa.", style="bold red")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=tipo_despesa_work.retorno,
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )
        await worker_sleep(5)
        
        try:
            console.print("[DESPESA] Verificando se existe tela de busca de tipo de despesa (TFrmBuscaGeralDialog)...", style="bold cyan")
            app_busca = Application(backend="win32").connect(class_name="TFrmBuscaGeralDialog")
            janela = app_busca.window(class_name="TFrmBuscaGeralDialog")
            janela.set_focus()
            janela.child_window(title="&Cancelar", class_name="TBitBtn").click()
            console.print("[DESPESA] Tela de busca de tipo de despesa encontrada. Tipo de despesa não localizado.", style="yellow")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno="Tipo de Despesa / conta contábil não localizado",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
            )
        except:
            console.print("[DESPESA] Tela de busca de tipo de despesa não apareceu. Seguindo fluxo normalmente.", style="cyan")
            pass

        await worker_sleep(3)

        # ================= ICMS HEADER =================
        console.print("[ICMS] Ativando checkbox 'Zerar ICMS'...", style="bold cyan")
        checkbox_zerar_icms = await zerar_icms()
        if checkbox_zerar_icms.sucesso:
            console.log(checkbox_zerar_icms.retorno, style="bold green")
        else:
            console.print("[ICMS] Falha na função zerar_icms.", style="bold red")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=checkbox_zerar_icms.retorno,
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )

        console.print("[ICMS] Definindo código ICMS conforme CFOP mapeado...", style="bold cyan")
        if cfop_key_escolhido == '1556':
            codigo_icms = '33'
        else:
            codigo_icms = '20'
        console.print(f"[ICMS] Código ICMS escolhido: {codigo_icms}", style="cyan")
        cod_icms_work = await cod_icms(codigo_icms)
        if cod_icms_work.sucesso:
            console.log(cod_icms_work.retorno, style="bold green")
        else:
            console.print("[ICMS] Falha na função cod_icms.", style="bold red")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=cod_icms_work.retorno,
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )

        await worker_sleep(3)

        console.print("[CFOP] Selecionando a opção 'Manter Natureza de Operação selecionada'...", style="bold cyan")
        checkbox = window.child_window(
            title="Manter Natureza de Operação selecionada",
            class_name="TDBICheckBox",
        )
        if not checkbox.get_toggle_state() == 1:
            checkbox.click()
            console.print("[CFOP] Opção 'Manter Natureza de Operação selecionada' marcada com sucesso.", style="bold green")
        else:
            console.print("[CFOP] Opção 'Manter Natureza de Operação selecionada' já estava marcada.", style="cyan")

        await worker_sleep(3)
        console.print("[CFOP] Clicando em OK para confirmar informações da importação...", style="bold cyan")

        max_attempts = 3
        i = 0
        while i < max_attempts:
            console.print(f"[CFOP] Tentativa {i+1}/{max_attempts} de clicar no botão OK...", style="cyan")
            try:
                try:
                    btn_ok = main_window.child_window(title="Ok")
                    btn_ok.click()
                    console.print("[CFOP] Clique no botão 'Ok' realizado.", style="cyan")
                except:
                    btn_ok = main_window.child_window(title="&Ok")
                    btn_ok.click()
                    console.print("[CFOP] Clique no botão '&Ok' realizado.", style="cyan")
            except:
                console.print("[CFOP] Não foi possível clicar no botão OK nesta tentativa.", style="yellow")

            await worker_sleep(3)

            try:
                informacao_nf_eletronica = await is_window_open(
                    "Informações para importação da Nota Fiscal Eletrônica"
                )
                if not informacao_nf_eletronica["IsOpened"]:
                    console.print("[CFOP] Tela de Informações para importação fechada. Prosseguindo...", style="bold green")
                    break
                else:
                    console.print("[CFOP] Tela ainda aberta após clique em OK.", style="yellow")
            except Exception as e:
                console.print(f"[CFOP] Erro ao verificar tela de informações: {e}. Tentativa {i+1}/{max_attempts}.", style="bold red")

            i += 1

        if i == max_attempts:
            msg = "Número máximo de tentativas atingido, Não foi possivel finalizar os trabalhos na tela de Informações para importação da Nota Fiscal Eletrônica"
            console.print(f"[CFOP] {msg}", style="bold red")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=msg,
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )

        await worker_sleep(10)

        # ================= ITENS =================
        console.print("[ITENS] Verificando pop-up de itens não localizados / NCM...", style="bold cyan")
        try:
            itens_by_supplier = await is_window_open_by_class("TFrmAguarde", "TMessageForm")
            console.print(f"[ITENS] Retorno is_window_open_by_class: {itens_by_supplier}", style="cyan")

            if itens_by_supplier["IsOpened"]:
                console.print("[ITENS] Pop-up de itens não localizados encontrado. Chamando itens_not_found_supplier...", style="yellow")
                itens_by_supplier_work = await itens_not_found_supplier(nota.get("nfe"))
                if not itens_by_supplier_work.sucesso:
                    console.print("[ITENS] Tratativa de itens não localizados retornou falha.", style="bold red")
                    return itens_by_supplier_work

        except Exception as error:
            console.print(f"[ITENS] Falha ao verificar POP-UP de itens não localizados: {error}", style="bold red")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=f"Falha ao verificar a existência de POP-UP de itens não localizados: {error}",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )

        await worker_sleep(10)
                
        console.print("[ITENS] Localizando botão 'Itens da Nota' via imagem...", style="bold cyan")
        imagem_itens = fr"{BASE_PATH}\itens_nota.png"
        tentativas_img = 0
        while True:
            tentativas_img += 1
            console.print(f"[ITENS] Tentativa {tentativas_img} de localizar itens_nota.png...", style="cyan")
            local = pyautogui.locateCenterOnScreen(imagem_itens, confidence=0.8)
            if local:
                pyautogui.click(local)
                console.print("[ITENS] Imagem 'itens_nota.png' encontrada e clicada com sucesso!", style="bold green")
                break
            else:
                console.print("[ITENS] Imagem 'itens_nota.png' não encontrada, tentando novamente...", style="yellow")
                time.sleep(1)

        await worker_sleep(3)
        console.print("[ITENS] Clicando em 'Itens da nota' por coordenada (fallback)...", style="cyan")
        pyautogui.click(791, 379)
        await worker_sleep(2)

        console.print("[ITENS] Obtendo índice do último item via get_ultimo_item()...", style="bold cyan")
        index_item_atual = 0
        index_ultimo_item = await get_ultimo_item()
        console.print(f"[ITENS] Index último item retornado: {index_ultimo_item}", style="bold green")
        
        try:
            console.print("[ITENS] Iniciando loop para tratar ICMS/IPI item a item...", style="bold cyan")
            while index_item_atual < index_ultimo_item:
                console.print(f"[ITENS] Início do processamento do item índice {index_item_atual+1}/{index_ultimo_item}...", style="cyan")
                send_keys("^({HOME})")
                await worker_sleep(1)

                if index_item_atual > 0:
                    send_keys("{DOWN " + str(index_item_atual) + "}")

                await worker_sleep(2)
                send_keys("+{F10}")
                await worker_sleep(1)
                send_keys("{DOWN 2}")
                await worker_sleep(1)
                send_keys("{ENTER}")

                await worker_sleep(2)
                app_alt = Application().connect(title="Alteração de Item")
                win_alt = app_alt["Alteração de Item"]
                win_alt.set_focus()

                _ = win_alt.child_window(class_name="TDBIEditCode", found_index=0)
                index_item_atual += 1
                console.print(f"[ITENS] Ítem atual no final da execução da tela: {index_item_atual}", style="cyan")
                await worker_sleep(1)

                lista_icms_090 = ["5101", "5102", "5103", "5104"]
                lista_icms_060 = ["5401", "5403", "5404", "5405", "6104", "6401", "6403", "6404", "6405"]

                console.print("[ITENS] Conectando na janela TFrmAlteraItemNFE para ajuste ICMS/IPI...", style="cyan")
                app_item = Application().connect(class_name="TFrmAlteraItemNFE")
                win_item = app_item["TFrmAlteraItemNFE"]
                win_item.set_focus()

                tipo_icms = win_item.child_window(class_name="TDBIComboBox", found_index=5)

                if cfop in lista_icms_090:
                    opcao_desejada = "090 - ICMS NACIONAL OUTRAS"
                elif cfop in lista_icms_060:
                    opcao_desejada = "060 - ICMS - SUBSTITUICAO TRIBUTARIA 060"
                else:
                    opcao_desejada = None

                console.print(f"[ITENS] CFOP item={cfop} | Opção ICMS desejada: {opcao_desejada}", style="cyan")

                if opcao_desejada:
                    try:
                        tipo_icms.select(opcao_desejada)
                        send_keys("{ENTER}")
                        console.print(f"[ITENS] Tipo ICMS '{opcao_desejada}' selecionado com sucesso.", style="bold green")
                    except Exception as e:
                        console.print(f"[ITENS] Erro ao selecionar opção ICMS no combobox: {e}", style="bold red")

                    combo_ipi = win_item.child_window(class_name="TDBIComboBox", found_index=4)
                    console.print("[ITENS] Selecionando IPI 0% no combobox de IPI...", style="cyan")
                    combo_ipi.select("IPI 0%")
                    console.print("[ITENS] IPI 0% selecionado com sucesso.", style="bold green")
                            
                    console.print("[ITENS] Clicando em 'Alterar' para confirmar mudanças do item...", style="cyan")
                    win_item.child_window(class_name="TDBIBitBtn", found_index=3).click()
                else:
                    console.print("[ITENS] Nenhuma opção ICMS mapeada para este CFOP de item. Item será mantido como está.", style="yellow")

                await worker_sleep(5)
        except Exception as e:
            console.print(f"[ITENS] Erro geral ao trabalhar nas alterações dos itens: {e}", style="bold red")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=f"Erro aotrabalhar nas alterações dos itens: {e}",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )

        console.print("[ITENS] Finalizado o tratamento de todos os itens. Verificando pop-up de confirmação TMessageForm...", style="bold cyan")
        try:
            app_msg = Application().connect(class_name="TMessageForm")
            win_msg = app_msg["TMessageForm"]
            btn_ok = win_msg.child_window(title="&Yes", class_name="TButton")
            btn_ok.click_input()
            console.print("[ITENS] Pop-up TMessageForm confirmado com &Yes.", style="bold green")
        except:
            console.print("[ITENS] Nenhum pop-up TMessageForm de confirmação encontrado. Seguindo...", style="cyan")
            pass
        await worker_sleep(10)
        
        # ===================== PAGAMENTOS =====================
        console.print("[PAGAMENTOS] Navegando pela janela de Nota Fiscal de Entrada (TFrmNotaFiscalEntrada)...", style="bold cyan")
        app_nf = Application().connect(class_name="TFrmNotaFiscalEntrada")
        nf_window = app_nf["TFrmNotaFiscalEntrada"]

        console.print("[PAGAMENTOS] Localizando aba 'Pagamentos' via imagem pagamentos.png...", style="bold cyan")
        img_pag = fr"{BASE_PATH}\pagamentos.png"

        tentativas_pag = 0
        while True:
            tentativas_pag += 1
            console.print(f"[PAGAMENTOS] Tentativa {tentativas_pag} de localizar 'pagamentos.png'...", style="cyan")
            local = pyautogui.locateCenterOnScreen(img_pag, confidence=0.9)
            if local:
                pyautogui.click(local)
                console.print("[PAGAMENTOS] Imagem 'pagamentos.png' encontrada e clicada com sucesso!", style="bold green")
                break
            else:
                console.print("[PAGAMENTOS] Imagem 'pagamentos.png' não encontrada, tentando novamente...", style="yellow")
                time.sleep(1)

        await worker_sleep(3)

        console.print("[PAGAMENTOS] Localizando combobox de Tipo de Cobrança na janela principal...", style="bold cyan")
        opcoes = [
            "BANCO DO BRASIL BOLETO FIDC",
            "BANCO DO BRASIL BOLETO",
            "BOLETO",
        ]
        console.print(f"[PAGAMENTOS] Ordem de preferência tipo de cobrança: {opcoes}", style="cyan")

        tipo_cobranca = None
        try:
            # primeiro chute: found_index=0 na janela principal
            tipo_cobranca = nf_window.child_window(class_name="TDBIComboBox", found_index=0)
            console.print("[PAGAMENTOS] Combobox de cobrança encontrado via found_index=0 na janela principal.", style="cyan")
        except Exception as e:
            console.print(f"[PAGAMENTOS] Falha ao localizar combobox de cobrança por found_index=0: {e}", style="yellow")
            tipo_cobranca = None

        if not tipo_cobranca:
            console.print("[PAGAMENTOS] Tentando localizar combobox correto de cobrança analisando todos os TDBIComboBox...", style="cyan")
            try:
                candidatos = nf_window.descendants(class_name="TDBIComboBox")
            except Exception as e:
                console.print(f"[PAGAMENTOS] Erro ao obter descendants TDBIComboBox: {e}", style="bold red")
                candidatos = []

            for i, combo in enumerate(candidatos):
                try:
                    itens_combo = [t.strip() for t in combo.item_texts() if str(t).strip()]
                    console.print(f"[PAGAMENTOS] Combo {i} itens encontrados: {itens_combo}", style="cyan")
                    texto_unico = " | ".join(itens_combo).lower()
                    if any(op.lower() in texto_unico for op in opcoes):
                        tipo_cobranca = combo
                        console.print(f"[PAGAMENTOS] Combo {i} escolhido como Tipo de Cobrança (contém alguma opção esperada).", style="bold green")
                        break
                except Exception as e:
                    console.print(f"[PAGAMENTOS] Erro ao ler itens do combo {i}: {e}", style="yellow")

        if not tipo_cobranca:
            raise RuntimeError("Não foi possível localizar o combobox de Tipo de Cobrança na janela de Nota Fiscal de Entrada.")

        # 1) Tenta select direto
        selecionado = None
        for alvo in opcoes:
            try:
                tipo_cobranca.select(alvo)
                if tipo_cobranca.window_text().strip().lower() == alvo.lower():
                    selecionado = alvo
                    console.print(f"[PAGAMENTOS] Tipo de cobrança selecionado diretamente via .select(): {alvo}", style="bold green")
                    break
            except Exception:
                console.print(f"[PAGAMENTOS] Falha ao selecionar opção '{alvo}' via .select(). Tentando próximas opções...", style="yellow")
                pass

        # 2) Fallback: HOME + DOWN lendo texto
        if not selecionado:
            console.print("[PAGAMENTOS] Tentando selecionar tipo de cobrança navegando com setas (HOME + DOWN)...", style="bold cyan")
            try:
                tipo_cobranca.set_focus()
                tipo_cobranca.click_input()
            except Exception as e:
                console.print(f"[PAGAMENTOS] Erro ao focar/clicar no combobox de cobrança: {e}", style="yellow")

            send_keys('{HOME}')
            vistos = set()
            for _ in range(80):
                atual = tipo_cobranca.window_text().strip()
                atual_lower = atual.lower()
                console.print(f"[PAGAMENTOS] Opção atualmente exibida no combo: '{atual}'", style="cyan")

                match = False
                for o in opcoes:
                    o_lower = o.lower()
                    if o_lower == atual_lower or o_lower in atual_lower:
                        match = True
                        selecionado = atual
                        break

                if match:
                    send_keys('{ENTER}')
                    console.print(f"[PAGAMENTOS] Tipo de cobrança selecionado via navegação por setas: '{selecionado}'", style="bold green")
                    break

                if atual_lower in vistos:
                    console.print("[PAGAMENTOS] Deu a volta na lista de tipos de cobrança. Abortando navegação.", style="yellow")
                    break

                vistos.add(atual_lower)
                send_keys('{DOWN}')

        erro_tipo = tipo_cobranca.window_text().strip()
        erro_tipo_lower = erro_tipo.lower()

        valido = False
        for o in opcoes:
            o_lower = o.lower()
            if o_lower == erro_tipo_lower or o_lower in erro_tipo_lower:
                valido = True
                break

        if not selecionado or not valido:
            console.print(
                f"[PAGAMENTOS] Não foi possível confirmar uma opção válida de cobrança. Ficou: '{erro_tipo}'",
                style="bold red"
            )
            raise RuntimeError(f"Não consegui selecionar uma opção válida. Ficou: '{erro_tipo}'")

        console.print(f"[PAGAMENTOS] Tipo de cobrança final selecionado: {erro_tipo}", style="bold green")

        # ========= DATA DE VENCIMENTO =========
        console.print("[PAGAMENTOS] Calculando e ajustando data de vencimento da parcela...", style="bold cyan")
        dt_vencimento_nota = nota.get("dataVencimento")
        data_atual_date = datetime.now().date()
        console.print(f"[PAGAMENTOS] Data vencimento original (configEntrada): {dt_vencimento_nota}", style="cyan")

        data_vencimento = datetime.strptime(dt_vencimento_nota, "%Y-%m-%d").date()

        if data_vencimento <= data_atual_date:
            console.print("[PAGAMENTOS] Data de vencimento original é hoje ou já passou. Ajustando para próximo dia útil...", style="yellow")
            data_vencimento = data_atual_date + timedelta(days=1)
            while data_vencimento.weekday() >= 5:
                data_vencimento += timedelta(days=1)

        data_vencimento_str = data_vencimento.strftime("%d/%m/%Y")
        console.print(f"[PAGAMENTOS] Nova data de vencimento calculada: {data_vencimento_str}", style="bold green")

        console.print("[PAGAMENTOS] Inserindo data de vencimento no campo TDBIEditDate (found_index=0)...", style="cyan")
        data_venc = nf_window.child_window(class_name="TDBIEditDate", found_index=0)
        data_venc.set_edit_text(data_vencimento_str)
        try:
            # Pegar valor 
            valor_ctrl = panel_TTabSheet.child_window(
                class_name="TDBIEditNumber",
                found_index=7
            )

            valor = valor_ctrl.window_text()
            console.print(valor)

            # Inserir valor 
            campo_destino = panel_TTabSheet.child_window(
                class_name="TDBIEditNumber",
                found_index=3
            )

            campo_destino.set_focus()
            campo_destino.select()                  # seleciona tudo
            campo_destino.type_keys("^a{BACKSPACE}") # limpa o campo
            campo_destino.type_keys(valor, with_spaces=True)

            # Clicar no + para incluir
            inserir_parcela = panel_TTabSheet.child_window(
                class_name="TDBIBitBtn",
                found_index=1
            ).click_input()
        except:
            pass
        
                         
        console.print(f"Incluindo registro...\n")
        try:
            inserir_registro = pyautogui.locateOnScreen("assets\\entrada_notas\\IncluirRegistro.png", confidence=0.8)
            pyautogui.click(inserir_registro)
            console.print("[PAGAMENTOS] Botão de 'Incluir Registro' clicado via imagem com sucesso.", style="bold green")
        except Exception as e:
            console.print(
                f"[PAGAMENTOS] Não foi possivel incluir o registro utilizando reconhecimento de imagem, Error: {e}...\n tentando inserir via posição...",
                style="yellow"
            )
            await incluir_registro()
            console.print("[PAGAMENTOS] Fallback incluir_registro() executado.", style="cyan")

        await worker_sleep(10)

        # ================= RATEIO / FINALIZAÇÃO =================
        console.print("[RATEIO] Tratando pop-ups e aguardando tela de Rateio da Despesa...", style="bold cyan")

        await worker_sleep(5)

        try:
            console.print("[RATEIO] Verificando POP-UP 'Itens que Ultrapassam a Variação Máxima de Custo'...", style="cyan")
            itens_variacao_maxima = await is_window_open_by_class("TFrmTelaSelecao", "TFrmTelaSelecao")
            console.print(f"[RATEIO] Retorno is_window_open_by_class para TFrmTelaSelecao: {itens_variacao_maxima}", style="cyan")

            if itens_variacao_maxima.get("IsOpened"):
                console.print("[RATEIO] Pop-up encontrado. Confirmando (ALT+O)...", style="yellow")
                app_sel = Application().connect(class_name="TFrmTelaSelecao")
                win_sel = app_sel["TFrmTelaSelecao"]
                win_sel.set_focus()
                send_keys("%o")
                console.print("[RATEIO] POP-UP tratado com sucesso.", style="bold green")
        except Exception as error:
            console.print(f"[RATEIO] Falha ao verificar POP-UP de variação máxima: {error}", style="bold red")

        await worker_sleep(2)

        console.print("[RATEIO] Verificando se a tela de 'Rateio da Despesa' já está aberta...", style="bold cyan")
        rateio_aberto = False
        try:
            rateio_win = Desktop(backend="uia").window(title_re=".*Rateio.*")
            rateio_aberto = rateio_win.exists(timeout=1)
            console.print(f"[RATEIO] Tela de rateio aberta? {rateio_aberto}", style="cyan")
        except Exception as e:
            console.print(f"[RATEIO] Erro ao verificar tela de rateio: {e}", style="yellow")
            rateio_aberto = False

        if not rateio_aberto:
            console.print("[RATEIO] Tela de rateio não aberta. Verificando Warning de soma pagamentos x valor da nota...", style="cyan")
            try:
                warning_app = Application().connect(title="Warning")
                warning_pop_up_pagamentos = warning_app["Warning"]
                existe_warning_pagamentos = warning_pop_up_pagamentos.exists(timeout=1)
            except Exception:
                existe_warning_pagamentos = False

            if existe_warning_pagamentos:
                console.print("[RATEIO] Warning encontrado: soma dos pagamentos não bate com o valor da nota.", style="bold red")
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno="A soma dos pagamentos não bate com o valor da nota.",
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                )
            else:
                console.print("[RATEIO] Warning de soma dos pagamentos não encontrado. Seguindo com o processo...", style="bold green")
        else:
            console.print("[RATEIO] Tela de Rateio da Despesa já está aberta. Ignorando validação de Warning de pagamentos.", style="cyan")

        console.print("[RATEIO] Aguardando a tela 'Rateio da Despesa'...", style="bold cyan")
        try:
            rateio_win = Desktop(backend="uia").window(title_re=".*Rateio.*")
            rateio_win.wait("exists enabled visible ready", timeout=30)
            console.print("[RATEIO] Tela 'Rateio da Despesa' encontrada. Prosseguindo com o rateio...", style="bold green")
        except Exception as e:
            console.print(f"[RATEIO] Erro ao aguardar tela de Rateio: {e}", style="bold red")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno="Número máximo de tentativas atingido. A tela para Rateio da Despesa não foi encontrada.",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )

        
        despesa_rateio_work = await rateio_despesa_centro_custo(centro_custo)
        if despesa_rateio_work.sucesso == True:
            console.log(despesa_rateio_work.retorno, style="bold green")
        else:
            console.print("[RATEIO] Falha ao executar rateio_despesa.", style="bold red")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=despesa_rateio_work.retorno,
                status=RpaHistoricoStatusEnum.Falha,
                tags=despesa_rateio_work.tags
            )

        console.print("[FINALIZAÇÃO] Aguardando warnings finais e validação da nota lançada...", style="bold cyan")
        await worker_sleep(15)
        warning_pop_up = await is_window_open("Warning")
        if warning_pop_up["IsOpened"]:
            console.print("[FINALIZAÇÃO] Pop-up 'Warning' encontrado no fim do fluxo. Capturando mensagem com OCR...", style="yellow")
            app_w = Application().connect(title="Warning")
            win_w = app_w["Warning"]
            win_w.set_focus()

            window_rect = win_w.rectangle()
            screenshot = pyautogui.screenshot(
                region=(window_rect.left, window_rect.top, window_rect.width(), window_rect.height())
            )
            username = getpass.getuser()
            path_to_png = f"C:\\Users\\{username}\\Downloads\\warning_popup_{nota.get('nfe')}.png"
            screenshot.save(path_to_png)
            console.print(f"[FINALIZAÇÃO] Print do Warning salvo em {path_to_png}", style="cyan")

            image = Image.open(path_to_png)
            image = image.convert("L")
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            image.save(path_to_png)
            console.print("[FINALIZAÇÃO] Imagem preparada. Iniciando OCR...", style="cyan")
            captured_text = pytesseract.image_to_string(Image.open(path_to_png))
            console.print(f"[FINALIZAÇÃO] Texto capturado do Warning: {captured_text}", style="bold green")
            os.remove(path_to_png)
            console.print("[FINALIZAÇÃO] Arquivo de imagem do Warning removido.", style="cyan")

            if 'movimento não permitido' in captured_text.lower():
                console.print("[FINALIZAÇÃO] Warning mapeado: movimento não permitido (livro fechado).", style="bold red")
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=f"Filial: {empresaCodigo} está com o livro fechado ou encerrado, verificar com o setor fiscal",
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                )
            else:
                console.print("[FINALIZAÇÃO] Warning não mapeado. Retornando como erro técnico com mensagem completa do OCR.", style="bold red")
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=f"Warning não mapeado para seguimento do robo, mensagem: {captured_text}",
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                )
            
        await worker_sleep(3)

        console.print("[FINALIZAÇÃO] Verificando se a nota foi lançada via check_nota_importada...", style="bold cyan")
        nf_imported = await check_nota_importada(dados_nf[0].get("chaveNfe"))
        console.print(f"[FINALIZAÇÃO] Retorno check_nota_importada: sucesso={nf_imported.sucesso} | retorno={nf_imported.retorno}", style="cyan")
        if nf_imported.sucesso:
            await worker_sleep(3)
            console.print("[FINALIZAÇÃO] Validando status da NF no EMSys via get_status_nf_emsys...", style="bold cyan")
            nf_chave_int = int(dados_nf[0].get("chaveNfe"))
            status_nf_emsys = await get_status_nf_emsys(nf_chave_int)
            console.print(f"[FINALIZAÇÃO] Status NF EMSys pós-lançamento: {status_nf_emsys}", style="cyan")
            if status_nf_emsys.get("status") == "Lançada":
                console.print("\n[FINALIZAÇÃO] Nota lançada com sucesso, processo finalizado...", style="bold green")
                return RpaRetornoProcessoDTO(
                    sucesso=True,
                    retorno="Nota Lançada com sucesso!",
                    status=RpaHistoricoStatusEnum.Sucesso,
                )
            else:
                console.print("[FINALIZAÇÃO] Pop-up nota incluída encontrado, porém status retornou diferente de 'Lançada'.", style="bold red")
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=f"Pop-up nota incluida encontrada, porém nota encontrada como 'já lançada' trazendo as seguintes informações: {nf_imported.retorno}",
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                )
        else:
            console.print("[FINALIZAÇÃO] check_nota_importada retornou falha. Nota não confirmada como lançada.", style="bold red")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=f"Erro ao lançar nota, erro: {nf_imported.retorno}",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )

    except Exception as ex:
        observacao = f"[ERRO GERAL] Erro Processo Entrada de Notas: {str(ex)}"
        logger.error(observacao)
        console.print(observacao, style="bold red")
        return RpaRetornoProcessoDTO(
            sucesso=False,
            retorno=observacao,
            status=RpaHistoricoStatusEnum.Falha,
            tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
        )

    finally:
        console.print("[FINALLY] Iniciando limpeza de XML (delete_xml)...", style="bold cyan")
        try:
            if numero_nota:
                await delete_xml(numero_nota)
                console.print(f"[FINALLY] XML da nota {numero_nota} deletado com sucesso.", style="bold green")
            else:
                console.print("[FINALLY] numero_nota é None, não foi possível chamar delete_xml com parâmetro válido.", style="yellow")
        except Exception as e:
            console.print(f"[FINALLY] Falha ao deletar XML da nota {numero_nota}: {e}", style="bold red")
        console.print("\n================ FIM PROCESSO opex_capex ================\n", style="bold blue")
