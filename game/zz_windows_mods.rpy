# Camada de compatibilidade local do Windows para PythonSDLActivity.
# As transacoes so acontecem quando a narrativa chama um metodo; nunca no overlay.

init 999 python:
    import re
    import time

    def dm_numero_inteiro(dm_valor, dm_padrao=0):
        try:
            if dm_valor is None:
                return dm_padrao
            return int(dm_valor)
        except (TypeError, ValueError, OverflowError):
            return dm_padrao


    def dm_booleano(dm_valor, dm_padrao=False):
        if dm_valor is None:
            return bool(dm_padrao)
        if isinstance(dm_valor, str):
            dm_texto = dm_valor.strip().lower()
            if dm_texto in ("", "0", "false", "nao", "não", "none"):
                return False
            if dm_texto in ("1", "true", "sim"):
                return True
        return bool(dm_valor)


    def dm_obter_store(dm_nome, dm_padrao=None):
        return getattr(store, dm_nome, dm_padrao)


    def dm_definir_store(dm_nome, dm_valor):
        setattr(store, dm_nome, dm_valor)
        return dm_valor


    def dm_obter_persistent(dm_nome, dm_padrao=None):
        return getattr(persistent, dm_nome, dm_padrao)


    def dm_salvar_persistent():
        renpy.save_persistent()


    def dm_definir_persistent(dm_nome, dm_valor, dm_salvar=True):
        setattr(persistent, dm_nome, dm_valor)
        if dm_salvar:
            dm_salvar_persistent()
        return dm_valor


    def dm_valor_arg(dm_padrao, dm_posicionais, dm_nome, dm_kwargs):
        if dm_nome in dm_kwargs:
            dm_valor = dm_kwargs[dm_nome]
        elif dm_posicionais:
            dm_valor = dm_posicionais[0]
        else:
            dm_valor = dm_padrao
        return dm_numero_inteiro(dm_valor, dm_padrao)


    def dm_cash_atualizar():
        dm_cash = max(0, dm_numero_inteiro(dm_obter_store("cash", 0)))
        dm_definir_store("cash", dm_cash)
        return dm_cash


    def dm_debitar_cash(dm_valor):
        dm_valor = dm_numero_inteiro(dm_valor, -1)
        dm_cash = dm_cash_atualizar()
        if dm_valor < 0 or dm_cash < dm_valor:
            return False
        return dm_definir_store("cash", dm_cash - dm_valor)


    def dm_adicionar_cash(dm_valor):
        dm_valor = dm_numero_inteiro(dm_valor, 0)
        dm_cash = dm_cash_atualizar()
        if dm_valor < 0:
            return dm_cash
        return dm_definir_store("cash", dm_cash + dm_valor)


    def dm_moedas_atualizar():
        dm_coins = max(0, dm_numero_inteiro(dm_obter_persistent("coins", 0)))
        if dm_obter_persistent("coins", None) != dm_coins:
            dm_definir_persistent("coins", dm_coins)
        return dm_coins


    def dm_debitar_moedas(dm_valor):
        dm_valor = dm_numero_inteiro(dm_valor, -1)
        dm_coins = dm_moedas_atualizar()
        if dm_valor < 0 or dm_coins < dm_valor:
            return False
        return dm_definir_persistent("coins", dm_coins - dm_valor)


    def dm_adicionar_moedas(dm_valor):
        dm_valor = dm_numero_inteiro(dm_valor, 0)
        dm_coins = dm_moedas_atualizar()
        if dm_valor < 0:
            return dm_coins
        return dm_definir_persistent("coins", dm_coins + dm_valor)


    def dm_progresso_contador(dm_persistent, dm_stores, dm_acrescimo=None, dm_limite=None):
        dm_valores = [max(0, dm_numero_inteiro(dm_obter_persistent(dm_persistent, 0)))]
        for dm_nome in dm_stores:
            dm_valores.append(max(0, dm_numero_inteiro(dm_obter_store(dm_nome, 0))))
        dm_atual = max(dm_valores)
        if dm_acrescimo is not None:
            dm_acrescimo = dm_numero_inteiro(dm_acrescimo, 0)
            if dm_acrescimo < 0:
                dm_acrescimo = 0
            dm_atual += dm_acrescimo
        if dm_limite is not None:
            dm_atual = min(dm_limite, dm_atual)
        for dm_nome in dm_stores:
            dm_definir_store(dm_nome, dm_atual)
        if dm_obter_persistent(dm_persistent, None) != dm_atual:
            dm_definir_persistent(dm_persistent, dm_atual)
        return dm_atual


    def dm_estado_persistente(dm_chave, dm_stores):
        dm_estado = dm_booleano(dm_obter_persistent(dm_chave, False))
        for dm_nome in dm_stores:
            dm_estado = dm_estado or dm_booleano(dm_obter_store(dm_nome, False))
        for dm_nome in dm_stores:
            dm_definir_store(dm_nome, dm_estado)
        if dm_estado and not dm_booleano(dm_obter_persistent(dm_chave, False)):
            dm_definir_persistent(dm_chave, True)
        return dm_estado


    def dm_comprar_desbloqueio(dm_preco, dm_chave, dm_stores, dm_persistent=None):
        dm_adquirido = dm_persistent and dm_booleano(dm_obter_persistent(dm_persistent, False))
        for dm_nome in dm_stores:
            dm_adquirido = dm_adquirido or dm_booleano(dm_obter_store(dm_nome, False))
        if dm_adquirido:
            for dm_nome in dm_stores:
                dm_definir_store(dm_nome, True)
            if dm_persistent and not dm_booleano(dm_obter_persistent(dm_persistent, False)):
                dm_definir_persistent(dm_persistent, True)
            return True

        dm_preco = dm_numero_inteiro(dm_preco, -1)
        if dm_preco <= 0 or dm_cash_atualizar() < dm_preco:
            return False

        dm_novo_cash = dm_debitar_cash(dm_preco)
        if dm_novo_cash is False:
            return False
        for dm_nome in dm_stores:
            dm_definir_store(dm_nome, True)
        if dm_persistent:
            dm_definir_persistent(dm_persistent, True)
        return True


    def dm_pega_cash(self, *args, **kwargs):
        return dm_cash_atualizar()


    def dm_ganha_cash(self, dm_quantidade=0, *args, **kwargs):
        return dm_adicionar_cash(dm_valor_arg(dm_quantidade, args, "quantidade", kwargs))


    def dm_usa_cash(self, dm_quantidade=0, *args, **kwargs):
        return dm_debitar_cash(dm_valor_arg(dm_quantidade, args, "quantidade", kwargs))


    def dm_pega_moedas(self, *args, **kwargs):
        return dm_moedas_atualizar()


    def dm_add_coins(self, dm_quantidade=0, *args, **kwargs):
        return dm_adicionar_moedas(dm_valor_arg(dm_quantidade, args, "quantidade", kwargs))


    def dm_comprar_cash_windows(dm_quantidade):
        dm_quantidade = dm_numero_inteiro(dm_quantidade, 0)
        dm_novo_saldo = dm_adicionar_cash(dm_quantidade)
        renpy.notify("Compra local concluida: CR$ %s adicionados. Saldo: CR$ %s." % (dm_quantidade, dm_novo_saldo))
        return dm_novo_saldo


    def dm_comprar_coins_windows(dm_quantidade=10000):
        dm_quantidade = dm_numero_inteiro(dm_quantidade, 0)
        dm_novo_saldo = dm_adicionar_moedas(dm_quantidade)
        renpy.notify("Compra local concluida: %s Celebrity Coins adicionadas." % dm_quantidade)
        return dm_novo_saldo


    def dm_usa_moedas(self, dm_quantidade=0, *args, **kwargs):
        return dm_debitar_moedas(dm_valor_arg(dm_quantidade, args, "quantidade", kwargs))


    def dm_comprar_blazer(self, *args, **kwargs):
        return dm_comprar_desbloqueio(250, "blazer", ("roupa_blazer",), "dm_roupa_blazer")


    def dm_pega_blazer(self, *args, **kwargs):
        return dm_estado_persistente("dm_roupa_blazer", ("roupa_blazer",))


    def dm_comprar_blacktie(self, *args, **kwargs):
        return dm_comprar_desbloqueio(1000, "blacktie", ("roupa_blacktie",), "dm_roupa_blacktie")


    def dm_pega_blacktie(self, *args, **kwargs):
        return dm_estado_persistente("dm_roupa_blacktie", ("roupa_blacktie",))


    def dm_comprar_casa(self, *args, **kwargs):
        return dm_comprar_desbloqueio(2000, "casa", ("casa", "casa_comprada"), "dm_casa_comprada")


    def dm_pega_casa(self, *args, **kwargs):
        return dm_estado_persistente("dm_casa_comprada", ("casa", "casa_comprada"))


    def dm_comprar_academia(self, *args, **kwargs):
        return dm_comprar_desbloqueio(250, "academia", ("academia",), "dm_academia")


    def dm_pega_academia(self, *args, **kwargs):
        return dm_estado_persistente("dm_academia", ("academia",))


    def dm_pega_fisico(self, *args, **kwargs):
        dm_pontos = max(0, dm_numero_inteiro(dm_obter_store("mc_fisico", 0)))
        dm_definir_store("mc_fisico", dm_pontos)
        return dm_pontos


    def dm_add_fisico(self, dm_quantidade=1, *args, **kwargs):
        dm_quantidade = dm_valor_arg(dm_quantidade, args, "quantidade", kwargs)
        if dm_quantidade < 0:
            return dm_pega_fisico(self)
        dm_pontos = dm_pega_fisico(self) + dm_quantidade
        dm_definir_store("mc_fisico", dm_pontos)
        return dm_pontos


    def dm_add_fisico_custom(self, dm_quantidade=0, *args, **kwargs):
        dm_quantidade = dm_valor_arg(dm_quantidade, args, "quantidade", kwargs)
        if dm_quantidade < 0:
            return dm_pega_fisico(self)
        return dm_add_fisico(self, dm_quantidade)


    def dm_pega_massage_points(self, *args, **kwargs):
        return dm_progresso_contador("dm_mc_massagem", ("mc_massagem", "mc_massagem_db"), dm_limite=10)


    def dm_mais_massage_points(self, *args, **kwargs):
        dm_local = max(
            0,
            dm_numero_inteiro(dm_obter_store("mc_massagem", 0)),
            dm_numero_inteiro(dm_obter_store("mc_massagem_db", 0)),
            dm_numero_inteiro(dm_obter_persistent("dm_mc_massagem", 0)),
        )
        dm_base = max(
            dm_numero_inteiro(dm_obter_store("mc_massagem", 0)),
            dm_numero_inteiro(dm_obter_store("mc_massagem_db", 0)),
        )
        dm_passo = 0 if dm_local > dm_base else 1
        return dm_progresso_contador("dm_mc_massagem", ("mc_massagem_db",), dm_passo, 10)


    def dm_pega_credito(self, *args, **kwargs):
        dm_credito = max(0, dm_numero_inteiro(dm_obter_store("credito", 0)))
        dm_definir_store("credito", dm_credito)
        return dm_credito


    def dm_pega_credito_total(self, *args, **kwargs):
        dm_total = max(0, dm_numero_inteiro(dm_obter_store("credito_total", 0)))
        dm_definir_store("credito_total", dm_total)
        return dm_total


    def dm_add_credito(self, dm_quantidade=0, dm_aposta=0, *args, **kwargs):
        dm_quantidade = dm_valor_arg(dm_quantidade, args, "quantidade", kwargs)
        dm_aposta = dm_numero_inteiro(kwargs.get("aposta", dm_aposta), -1)
        if dm_quantidade < 0 or dm_aposta < 0:
            return False
        dm_credito = dm_pega_credito(self)
        if dm_credito < dm_aposta:
            return False
        dm_definir_store("credito", dm_credito - dm_aposta + dm_quantidade)
        if dm_quantidade > 0:
            dm_definir_store("credito_total", dm_pega_credito_total(self) + dm_quantidade)
        return dm_pega_credito(self)


    def dm_ganha_credito(self, dm_quantidade=0, *args, **kwargs):
        dm_quantidade = dm_valor_arg(dm_quantidade, args, "quantidade", kwargs)
        if dm_quantidade < 0:
            return dm_pega_credito(self)
        dm_definir_store("credito", dm_pega_credito(self) + dm_quantidade)
        dm_definir_store("credito_total", dm_pega_credito_total(self) + dm_quantidade)
        return dm_pega_credito(self)


    def dm_usa_credito(self, dm_quantidade=0, *args, **kwargs):
        dm_quantidade = dm_valor_arg(dm_quantidade, args, "quantidade", kwargs)
        dm_credito = dm_pega_credito(self)
        if dm_quantidade < 0 or dm_credito < dm_quantidade:
            return False
        dm_definir_store("credito", dm_credito - dm_quantidade)
        return dm_pega_credito(self)


    def dm_compra_credito(self, dm_quantidade=0, *args, **kwargs):
        dm_quantidade = dm_valor_arg(dm_quantidade, args, "quantidade", kwargs)
        if dm_quantidade <= 0 or dm_cash_atualizar() < dm_quantidade:
            return False
        if dm_debitar_cash(dm_quantidade) is False:
            return False
        dm_definir_store("credito", dm_pega_credito(self) + dm_quantidade)
        return dm_pega_credito(self)


    def dm_troca_credito(self, dm_quantidade=0, *args, **kwargs):
        dm_quantidade = dm_valor_arg(dm_quantidade, args, "quantidade", kwargs)
        dm_credito = dm_pega_credito(self)
        if dm_quantidade <= 0 or dm_credito < dm_quantidade:
            return False
        dm_definir_store("credito", dm_credito - dm_quantidade)
        dm_adicionar_cash(dm_quantidade)
        return True


    def dm_salvar_jogo(self, *args, **kwargs):
        dm_definir_store("salvado", True)
        return True


    def dm_pega_salvado(self, *args, **kwargs):
        return dm_booleano(dm_obter_store("salvado", True), True)


    def dm_seta_salvado(self, *args, **kwargs):
        return dm_definir_store("salvado", True)


    def dm_pega_guia1(self, *args, **kwargs):
        return dm_booleano(dm_obter_persistent("guia1", False))


    def dm_compra_guia1(self, *args, **kwargs):
        if dm_pega_guia1(self):
            return True
        if dm_debitar_moedas(300) is False:
            return False
        dm_definir_persistent("guia1", True)
        return True


    def dm_ganha_carta(self, dm_carta=None, *args, **kwargs):
        dm_id = dm_numero_inteiro(dm_carta if dm_carta is not None else (args[0] if args else None), -1)
        dm_validos = {1, 2, 3, 4, 5} | set(range(501, 511)) | set(range(1001, 1016))
        if dm_id not in dm_validos:
            return False
        dm_nome = "card_%s" % dm_id
        dm_definir_persistent(dm_nome, True)
        return True


    def dm_compra_carta(self, dm_carta=None, *args, **kwargs):
        dm_id = dm_numero_inteiro(dm_carta if dm_carta is not None else (args[0] if args else None), -1)
        dm_validos = {1, 2, 3, 4, 5} | set(range(501, 511)) | set(range(1001, 1016))
        if dm_id not in dm_validos:
            return False
        if dm_debitar_moedas(10) is False:
            return False
        dm_definir_persistent("card_%s" % dm_id, True)
        return True


    def dm_pega_carta(dm_id):
        dm_id = dm_numero_inteiro(dm_id, -1)
        dm_validos = {1, 2, 3, 4, 5} | set(range(501, 511)) | set(range(1001, 1016))
        if dm_id not in dm_validos:
            return False
        return dm_booleano(dm_obter_persistent("card_%s" % dm_id, False))


    def dm_pega_carta_method(dm_id):
        def dm_metodo(self, *args, **kwargs):
            return dm_pega_carta(dm_id)
        return dm_metodo


    def dm_libera_aula_mas(self, *args, **kwargs):
        # Windows already bypasses the real-time wait; charging for this has no effect.
        return False


    def dm_pega_livros(self, *args, **kwargs):
        return dm_progresso_contador("dm_livros_liberados", ("livros_liberados_db",))


    def dm_add_livros(self, *args, **kwargs):
        dm_atual = dm_pega_livros(self)
        if dm_atual >= 5:
            return False
        if dm_debitar_cash(250) is False:
            return False
        dm_novo = dm_progresso_contador("dm_livros_liberados", ("livros_liberados_db",), 1, 5)
        return dm_novo


    def dm_pega_bao(self, *args, **kwargs):
        return dm_progresso_contador("dm_bao_pontos", ("bao_pontos",))


    def dm_add_bao(self, dm_quantidade=0, *args, **kwargs):
        dm_quantidade = dm_valor_arg(dm_quantidade, args, "quantidade", kwargs)
        return dm_progresso_contador("dm_bao_pontos", ("bao_pontos",), max(0, dm_quantidade))


    def dm_pega_banho(self, *args, **kwargs):
        return dm_progresso_contador("dm_banho_eventos", ("banho_evento_db",))


    def dm_add_banho(self, *args, **kwargs):
        return dm_progresso_contador("dm_banho_eventos", ("banho_evento_db",), 1)


    def dm_pega_distrito(self, *args, **kwargs):
        return dm_progresso_contador("dm_distrito_pagamentos", ("distrito_db",))


    def dm_add_distrito(self, *args, **kwargs):
        return dm_progresso_contador("dm_distrito_pagamentos", ("distrito_db",), 1)


    def dm_pega_xiang(self, *args, **kwargs):
        return dm_progresso_contador("dm_xiang_eventos", ("xiang_evento_db",))


    def dm_add_xiang(self, *args, **kwargs):
        return dm_progresso_contador("dm_xiang_eventos", ("xiang_evento_db",), 1)


    def dm_add_pauta_cassia(self, *args, **kwargs):
        return dm_progresso_contador("dm_pauta_cassia", ("pauta_cassia_db",), 1)


    def dm_pega_pauta_cassia(self, *args, **kwargs):
        return dm_progresso_contador("dm_pauta_cassia", ("pauta_cassia_db",))


    def dm_add_thaynara(self, *args, **kwargs):
        return dm_progresso_contador("dm_thaynara_eventos", ("thaynara_db",), 1)


    def dm_pega_thaynara(self, *args, **kwargs):
        return dm_progresso_contador("dm_thaynara_eventos", ("thaynara_db",))


    def dm_pega_pauta(self, *args, **kwargs):
        return dm_estado_persistente("dm_pauta_fabricio", ("pauta_fabricio",))


    def dm_compra_pauta(self, *args, **kwargs):
        return dm_comprar_desbloqueio(250, "pauta", ("pauta_fabricio",), "dm_pauta_fabricio")


    def dm_pega_carro(self, *args, **kwargs):
        return dm_estado_persistente("dm_carro", ("carro",))


    def dm_compra_carro(self, *args, **kwargs):
        return dm_comprar_desbloqueio(2000, "carro", ("carro",), "dm_carro")


    def dm_pega_roupa_nathan(self, *args, **kwargs):
        return dm_estado_persistente("dm_roupa_nathan", ("roupa_nathan",))


    def dm_compra_roupa_nathan(self, *args, **kwargs):
        return dm_comprar_desbloqueio(250, "uniforme_nathan", ("roupa_nathan",), "dm_roupa_nathan")


    def dm_pega_fadolandia(self, *args, **kwargs):
        return dm_progresso_contador("dm_fadolandia_visitas", ("fadolandia_db",))


    def dm_pega_natasha(self, *args, **kwargs):
        return dm_progresso_contador("dm_natasha_visitas", ("natasha_db",))


    def dm_pega_sofia(self, *args, **kwargs):
        return dm_progresso_contador("dm_sofia_visitas", ("sofia_db",))


    def dm_pega_praia(dm_nome, dm_store):
        def dm_metodo(self, *args, **kwargs):
            return dm_estado_persistente("dm_praia_%s" % dm_nome, (dm_store,))
        return dm_metodo


    def dm_compra_praia(dm_nome, dm_store):
        def dm_metodo(self, *args, **kwargs):
            return dm_comprar_desbloqueio(200, "praia_%s" % dm_nome, (dm_store,), "dm_praia_%s" % dm_nome)
        return dm_metodo


    def dm_compra_slot_credito(self, dm_quantidade=0, *args, **kwargs):
        return dm_compra_credito(self, dm_quantidade, *args, **kwargs)


    def dm_timer_true(self, *args, **kwargs):
        return True


    def dm_timer_zero(self, *args, **kwargs):
        return 0


    def dm_acertar_ep(dm_numero):
        def dm_metodo(self, *args, **kwargs):
            return dm_definir_persistent("dm_ep_p%s" % dm_numero, True)
        return dm_metodo


    def dm_pega_ep_resposta(dm_numero):
        def dm_metodo(self, *args, **kwargs):
            return dm_booleano(dm_obter_persistent("dm_ep_p%s" % dm_numero, False))
        return dm_metodo


    def dm_pega_ep_pontos(self, *args, **kwargs):
        return dm_progresso_contador("dm_ep_pontos", ("ep_pontos",))


    def dm_ganha_ep_pontos(self, *args, **kwargs):
        return dm_progresso_contador("dm_ep_pontos", ("ep_pontos",), 1)


    def dm_carregar_conta_local_windows():
        dm_carregar = getattr(store, "dm_carregar_conta_windows", None)
        if callable(dm_carregar):
            dm_carregar()

    def dm_pega_logado_windows(self, *args, **kwargs):
        dm_carregar_conta_local_windows()
        return bool(dm_obter_store("userlogado", False))

    def dm_pega_email_windows(self, *args, **kwargs):
        dm_carregar_conta_local_windows()
        return str(dm_obter_store("useremail", "") or "")

    def dm_pega_uid_windows(self, *args, **kwargs):
        dm_carregar_conta_local_windows()
        if dm_pega_logado_windows(self):
            return getattr(store, "DM_UID_CONTA_WINDOWS", "windows_local_mafra_360")
        return None

    def dm_abre_login_windows(self, *args, **kwargs):
        dm_salvar = getattr(store, "dm_salvar_conta_windows", None)
        dm_email = getattr(store, "DM_EMAIL_CONTA_WINDOWS", "")
        if callable(dm_salvar) and dm_email:
            dm_salvar(dm_email)
        renpy.restart_interaction()
        return dm_pega_logado_windows(self)

    def dm_modo_externo_neutro(self, *args, **kwargs):
        return None


    def dm_log_desconhecido(dm_nome):
        try:
            if renpy.config.developer:
                renpy.log("PythonSDLActivity offline: metodo sem adaptador: %s" % dm_nome)
        except Exception:
            pass


    def dm_metodo_desconhecido(self, dm_nome):
        def dm_chamada(*args, **kwargs):
            dm_log_desconhecido(dm_nome)
            if dm_nome in ("loadAD", "loadVID", "registraEvento", "salvaHist"):
                return None
            if dm_nome.startswith("pegaCarta"):
                dm_sufixo = dm_nome[len("pegaCarta"):]
                if dm_sufixo.isdigit():
                    dm_valor = dm_pega_carta(dm_sufixo)
                    if dm_numero_inteiro(dm_sufixo, -1) not in ({1, 2, 3, 4, 5} | set(range(501, 511)) | set(range(1001, 1016))):
                        dm_log_desconhecido(dm_nome)
                    return dm_valor
            return False
        return dm_chamada


    def dm_set_daily(self, *args, **kwargs):
        if not dm_booleano(dm_obter_persistent("daily", False)):
            dm_definir_persistent("daily", True)
        return True


    def dm_instalar_adaptador_windows():
        if renpy.android:
            return
        dm_atividade = dm_obter_store("PythonSDLActivity", None)
        if dm_atividade is None:
            return
        dm_classe = dm_atividade.__class__

        dm_metodos = {
            "pegaCash": dm_pega_cash,
            "ganhaCash": dm_ganha_cash,
            "usaCash": dm_usa_cash,
            "pegaMoedas": dm_pega_moedas,
            "addCoins": dm_add_coins,
            "usaMoedas": dm_usa_moedas,
            "compraBlazer": dm_comprar_blazer,
            "pegaBlazer": dm_pega_blazer,
            "compraBlacktie": dm_comprar_blacktie,
            "pegaBlacktie": dm_pega_blacktie,
            "compraCasa": dm_comprar_casa,
            "pegaCasa": dm_pega_casa,
            "compraAcademia": dm_comprar_academia,
            "pegaAcademia": dm_pega_academia,
            "pegaFpontos": dm_pega_fisico,
            "addFpontos": dm_add_fisico,
            "addFCustomPontos": dm_add_fisico_custom,
            "pegaMpontos": dm_pega_massage_points,
            "maisMpontos": dm_mais_massage_points,
            "pegaCredito": dm_pega_credito,
            "pegaCreditoTotal": dm_pega_credito_total,
            "addCredito": dm_add_credito,
            "ganhaCredito": dm_ganha_credito,
            "usaCredito": dm_usa_credito,
            "compraCredito": dm_compra_slot_credito,
            "trocaCredito": dm_troca_credito,
            "salvaJogo": dm_salvar_jogo,
            "pegaSalvado": dm_pega_salvado,
            "setaSalvado": dm_seta_salvado,
            "pegaGuia1": dm_pega_guia1,
            "compraGuia1": dm_compra_guia1,
            "ganhaCarta": dm_ganha_carta,
            "compraCarta": dm_compra_carta,
            "liberaAulaMas": dm_libera_aula_mas,
            "pegaLivros": dm_pega_livros,
            "addLivros": dm_add_livros,
            "pegaBao": dm_pega_bao,
            "addBao": dm_add_bao,
            "pegaBanho": dm_pega_banho,
            "addBanho": dm_add_banho,
            "pegaDistrito": dm_pega_distrito,
            "addDistrito": dm_add_distrito,
            "pegaXiang": dm_pega_xiang,
            "addXiang": dm_add_xiang,
            "pegaPautaCassia": dm_pega_pauta_cassia,
            "addPautaCassia": dm_add_pauta_cassia,
            "pegaThaynara": dm_pega_thaynara,
            "addThaynara": dm_add_thaynara,
            "pegaPauta": dm_pega_pauta,
            "compraPauta": dm_compra_pauta,
            "pegaCarro": dm_pega_carro,
            "compraCarro": dm_compra_carro,
            "pegaRoupaNathan": dm_pega_roupa_nathan,
            "compraRoupaNathan": dm_compra_roupa_nathan,
            "pegaFadolandia": dm_pega_fadolandia,
            "pegaNatasha": dm_pega_natasha,
            "pegaSofia": dm_pega_sofia,
            "pegaEPpontos": dm_pega_ep_pontos,
            "ganhaEPpontos": dm_ganha_ep_pontos,
            "tempoAgora": lambda self, *args, **kwargs: int(time.time()),
            "pegaUid": dm_pega_uid_windows,
            "pegaVID": dm_modo_externo_neutro,
            "loadVID": dm_modo_externo_neutro,
            "pegaEmail": dm_pega_email_windows,
            "pegaLogado": dm_pega_logado_windows,
            "abreLogin": dm_abre_login_windows,
            # Politica da edicao Windows offline: conteudo narrativo local liberado;
            # este valor nao representa validacao de apoiador por servidor.
            "pegaBacker": lambda self, *args, **kwargs: True,
            "pegaBanned": lambda self, *args, **kwargs: False,
            "registraEvento": dm_modo_externo_neutro,
            "loadAD": lambda self, *args, **kwargs: False,
            "pegaAnuncio": lambda self, *args, **kwargs: False,
            "salvaHist": dm_modo_externo_neutro,
            "setDaily": dm_set_daily,
            "checkDailyNext": dm_timer_true,
            "checaTempo": dm_timer_true,
            "iniciaVariaveis": dm_timer_true,
        }
        for dm_nome, dm_funcao in dm_metodos.items():
            setattr(dm_classe, dm_nome, dm_funcao)

        dm_classe.__getattr__ = dm_metodo_desconhecido
        for dm_nome in ("mtempo", "mttempo", "tbtempo", "tltempo", "ftempo", "etempo", "ntempo", "stempo", "checatempo"):
            setattr(store, dm_nome, True)
        for dm_id in [1, 2, 3, 4, 5] + list(range(501, 511)) + list(range(1001, 1016)):
            setattr(dm_classe, "pegaCarta%s" % dm_id, dm_pega_carta_method(dm_id))

        dm_praias = {
            "Priscila": "praia_priscila",
            "Sayuri": "praia_sayuri",
            "Julia": "praia_julia",
            "Diana": "praia_diana",
            "Nathan": "praia_nathan",
            "Sofia": "praia_sofia",
            "Natasha": "praia_natasha",
            "Nona": "praia_nona",
        }
        for dm_nome, dm_store in dm_praias.items():
            setattr(dm_classe, "pegaPraia%s" % dm_nome, dm_pega_praia(dm_nome.lower(), dm_store))
            setattr(dm_classe, "compraPraia%s" % dm_nome, dm_compra_praia(dm_nome.lower(), dm_store))

        for dm_numero in range(1, 11):
            setattr(dm_classe, "acertaEPp%s" % dm_numero, dm_acertar_ep(dm_numero))
            setattr(dm_classe, "pegaEPp%s" % dm_numero, dm_pega_ep_resposta(dm_numero))

        for dm_nome in (
            "checkMtempoNext", "checkMTtempoNext", "checkTBtempoNext",
            "checkTLtempoNext", "checkFtempoNext", "checkEPtempoNext",
            "checkNtempoNext", "checkStempoNext", "checkMasTempoNext",
            "checkTrabalhoTempoNext", "checkDailyNext", "checaTempo",
            "setMtempoNext", "setMTtempoNext", "setTBtempoNext",
            "setTLtempoNext", "setFtempoNext", "setEPtempoNext",
            "setNtempoNext", "setStempoNext", "setMasTempoNext",
            "setTrabalhoTempoNext", "setMtempo", "avancaEPTempo",
            "avancaFTempo", "avancaMasTempo", "avancaMTTempo",
            "avancaNTempo", "avancaSTempo", "avancaTLTempo",
        ):
            setattr(dm_classe, dm_nome, dm_timer_true)

        for dm_nome in (
            "pegaEPNext", "pegaFNext", "pegaMasNext", "pegaMTNext",
            "pegaNNext", "pegaSNext", "pegaTBNext", "pegaTLNext",
            "getMtempoNext", "pegaTempo",
        ):
            setattr(dm_classe, dm_nome, dm_timer_zero)

        dm_instalar_slots_windows(dm_classe)


    def dm_instalar_slots_windows(dm_classe):
        if renpy.android:
            return
        # credito e credito_total pertencem ao save atual; nada e copiado para persistent.
        dm_classe.salvaJogo = dm_salvar_jogo
        dm_classe.pegaSalvado = dm_pega_salvado
        dm_classe.setaSalvado = dm_seta_salvado


    dm_instalar_adaptador_windows()



# ============================================================
# JULIA: INVESTIGACAO SEM FALHA
# ============================================================
#
# Substitui o label j3_calculo sem modificar julia.rpy.
#
# A porcentagem visual continua diminuindo:
# 100%, 90%, 80%... 10%, 0%.
#
# A investigacao, entretanto, sempre termina com sucesso,
# inclusive quando a chance exibida chegar a zero.
# ============================================================


init 1000 python:

    # Redireciona qualquer call ou jump para j3_calculo
    # ao label alternativo deste mod.
    config.label_overrides["j3_calculo"] = (
        "dm_j3_calculo_sempre_sucesso"
    )


label dm_j3_calculo_sempre_sucesso:

    # Mantem o calculo original da dificuldade.
    $ j3_dificuldade = 10 * j3_xereta

    # A porcentagem nunca aparece como numero negativo.
    $ j3_chance = max(
        0,
        100 - j3_dificuldade
    )

    if j3_xereta == 0:

        "{b}Você ainda não investigou a [g] nenhuma vez.{/b}"

        "{b}Sua chance de conseguir xeretar ela agora sem ser descoberto é de [j3_chance] por cento.{/b}"

    elif j3_xereta == 1:

        "{b}Você investigou a [g] uma vez.{/b}"

        "{b}Sua chance de conseguir xeretar ela agora sem ser descoberto é de [j3_chance] por cento.{/b}"

    else:

        "{b}Você investigou a [g] [j3_xereta] vezes.{/b}"

        "{b}Sua chance de conseguir xeretar ela agora sem ser descoberto é de [j3_chance] por cento.{/b}"

    mc desculpa "{size=15}Preciso fazer isso com muito calma. Ela não pode me ver, ou minha investigação acaba.{/size}"

    "{size=15}Com muita calma agora...{/size}"

    # Preserva a variável usada pelo evento, mas força sucesso.
    $ randj3 = 0

    # Registra mais uma investigação bem-sucedida.
    $ j3_xereta += 1

    play sound "extra/carta.mp3"

    "{size=15}Ufa! Estou seguro. Ela não me viu...{/size}"

    return


# ============================================================
# JULIA: PROPOSTA DO CAIO + RESGATE DA MESA
# ============================================================
#
# Quando a rota registrar julia_e4 = "caio", o mod tambem
# registra que Julia foi retirada da mesa.
#
# A funcao e idempotente: nao altera dinheiro, pontos,
# recompensas ou a rota escolhida.
# ============================================================

# init 1001 python:

#     def dm_julia_evento4_resultado_combinado():
#         if renpy.android:
#             return

#         if getattr(store, "julia_e4", None) == "caio":
#             store.j4_salvou = True


#     if (
#         dm_julia_evento4_resultado_combinado
#         not in config.overlay_functions
#     ):
#         config.overlay_functions.append(
#             dm_julia_evento4_resultado_combinado
#         )


# Conta local Windows. Sem autenticacao externa.
define DM_EMAIL_CONTA_WINDOWS = "mafra_360@hotmail.com"
define DM_UID_CONTA_WINDOWS = "windows_local_mafra_360"
default dm_erro_conta_windows = ""
default persistent.dm_userlogado_windows = False
default persistent.dm_useremail_windows = ""

init -100 python:
    def dm_salvar_conta_windows(dm_email=None):
        email = DM_EMAIL_CONTA_WINDOWS if dm_email is None else str(dm_email).strip().lower()
        if email != DM_EMAIL_CONTA_WINDOWS:
            return False
        if not getattr(persistent, "dm_userlogado_windows", False) or getattr(persistent, "dm_useremail_windows", "") != email:
            persistent.dm_userlogado_windows = True
            persistent.dm_useremail_windows = email
            renpy.save_persistent()
        store.userlogado = True
        store.useremail = email
        store.email = email
        store.uid = DM_UID_CONTA_WINDOWS
        store.dm_erro_conta_windows = ""
        return True

    def dm_carregar_conta_windows():
        if renpy.android:
            return False
        if getattr(persistent, "dm_userlogado_windows", False) and getattr(persistent, "dm_useremail_windows", "") == DM_EMAIL_CONTA_WINDOWS:
            store.userlogado = True
            store.useremail = DM_EMAIL_CONTA_WINDOWS
            store.email = DM_EMAIL_CONTA_WINDOWS
            store.uid = DM_UID_CONTA_WINDOWS
            return True
        return dm_salvar_conta_windows(DM_EMAIL_CONTA_WINDOWS)

    def dm_conta_windows_correta():
        return bool(store.userlogado and store.useremail == DM_EMAIL_CONTA_WINDOWS)

    def dm_sair_conta_windows():
        if getattr(persistent, "dm_userlogado_windows", False) or getattr(persistent, "dm_useremail_windows", ""):
            persistent.dm_userlogado_windows = False
            persistent.dm_useremail_windows = ""
            renpy.save_persistent()
        store.userlogado = False
        store.useremail = ""
        store.email = ""
        store.uid = "NOID"
        renpy.restart_interaction()
        return True

init 100 python:
    dm_carregar_conta_windows()

screen dm_bloco_conta_windows():
    vbox:
        xalign 0.5
        spacing 6
        text "Conta" xalign 0.5
        if userlogado:
            text "E-mail: [useremail]" size 14 xalign 0.5
            textbutton "Sair da conta" action Function(dm_sair_conta_windows)
        else:
            imagebutton auto "extra/botao_login_%s.png" action Function(dm_salvar_conta_windows, DM_EMAIL_CONTA_WINDOWS)

screen celular_mc():
    tag celular
    zorder 100
    modal True
    predict False
    on "show" action Function(dm_carregar_conta_windows)
    python:
        persistent.coins = PythonSDLActivity.pegaMoedas(0)
        cash = PythonSDLActivity.pegaCash()
        mc_fisico = PythonSDLActivity.pegaFpontos()
        bao_pontos = PythonSDLActivity.pegaBao()
        if userlogado:
            useremail = PythonSDLActivity.pegaEmail()
    imagemap:
        xalign 0.5
        yalign 0.5
        auto "extra/celular_%s.png"
        hotspot (160, 635, 50, 55) action Hide("celular_mc")
    frame:
        xsize 364
        ysize 620
        left_padding 20
        right_padding 40
        top_padding 30
        bottom_padding 0
        xalign 0.5
        background None
        has frame
        xsize 304
        ysize 590
        top_margin 45
        left_margin 5
        background "celular/android-fundo.jpg"
        vbox:
            xalign 0.5
            xanchor 0.5
            spacing 30
            vbox:
                xalign 0.5
                xanchor 0.5
                add "extra/celular_botao_mc_idle.png" at center
                text "[mcc]" size 18
            hbox:
                spacing 50
                xalign 0.5
                xanchor 0.5
                vbox:
                    spacing 5
                    add "extra/coin_25.png" xalign 0.5 xanchor 0.5
                    text "[persistent.coins]" size 14 xalign 0.5 xanchor 0.5
                vbox:
                    spacing 5
                    add "extra/money.png" xalign 0.5 xanchor 0.5
                    text "[cash]" size 14 xalign 0.5 xanchor 0.5
            text "Habilidades" xalign 0.5 xanchor 0.5 size 18
            vbox:
                spacing 5
                text "Massagem: [mc_massagem]/10" size 14
                text "Físico: [mc_fisico]/500" size 14
                text "Bao Chang: [bao_pontos]/300" size 14
            if renpy.android:
                text "Conta" xalign 0.5 xanchor 0.5 size 18
                if userlogado:
                    text "E-mail: [useremail]" size 14
                else:
                    imagebutton auto "extra/botao_login_%s.png" xalign 0.5 xanchor 0.5 action Call("fazer_login")
            else:
                use dm_bloco_conta_windows

screen celular_mc_copia():
    tag celular
    zorder 100
    modal True
    predict False
    on "show" action Function(dm_carregar_conta_windows)
    python:
        persistent.coins = PythonSDLActivity.pegaMoedas(0)
        cash = PythonSDLActivity.pegaCash()
        mc_fisico = PythonSDLActivity.pegaFpontos()
        bao_pontos = PythonSDLActivity.pegaBao()
        if userlogado:
            useremail = PythonSDLActivity.pegaEmail()
    imagemap:
        xalign 0.5
        yalign 0.5
        auto "extra/celular_%s.png"
        hotspot (160, 635, 50, 55) action Hide("celular_mc_copia")
    frame:
        xsize 364
        ysize 620
        left_padding 20
        right_padding 40
        top_padding 30
        bottom_padding 0
        xalign 0.5
        background None
        has frame
        xsize 304
        ysize 590
        top_margin 45
        left_margin 5
        background "celular/android-fundo.jpg"
        vbox:
            xalign 0.5
            xanchor 0.5
            spacing 30
            vbox:
                xalign 0.5
                xanchor 0.5
                add "extra/celular_botao_mc_idle.png" at center
                text "[mcc]" size 18
            hbox:
                spacing 50
                xalign 0.5
                xanchor 0.5
                vbox:
                    spacing 5
                    add "extra/coin_25.png" xalign 0.5 xanchor 0.5
                    text "[persistent.coins]" size 14 xalign 0.5 xanchor 0.5
                vbox:
                    spacing 5
                    add "extra/money.png" xalign 0.5 xanchor 0.5
                    text "[novo_cash]" size 14 xalign 0.5 xanchor 0.5
            text "Habilidades" xalign 0.5 xanchor 0.5 size 18
            vbox:
                spacing 5
                text "Massagem: [mc_massagem]/10" size 14
                text "Físico: [mc_fisico]/500" size 14
                text "Bao Chang: [bao_pontos]/300" size 14
            if renpy.android:
                text "Conta" xalign 0.5 xanchor 0.5 size 18
                if userlogado:
                    text "E-mail: [useremail]" size 14
                else:
                    imagebutton auto "extra/botao_login_%s.png" xalign 0.5 xanchor 0.5 action Call("fazer_login")
            else:
                use dm_bloco_conta_windows
