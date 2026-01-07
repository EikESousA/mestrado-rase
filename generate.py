def _get_active_names(options):
    return [name for name, active in options if active]


def generate_data(ns, models):
    active_ns = _get_active_names(ns)
    active_models = _get_active_names(models)

    if not active_ns:
        print("Selecione o N1, N2 ou N3 para gerar os dados.")
        print()
        input("Digite qualquer tecla para voltar ao menu.")
        return

    if not active_models:
        print("Selecione o Alpaca, Dolphin ou LLaMa para gerar os dados.")
        print()
        input("Digite qualquer tecla para voltar ao menu.")
        return

    print("Dados Gerados")
    print("N selecionados: {}".format(", ".join(active_ns)))
    print("Modelos selecionados: {}".format(", ".join(active_models)))
		print()
    input("Digite qualquer tecla para voltar ao menu.")
