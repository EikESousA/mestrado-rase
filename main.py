def main():
    while True:
        print("1 - Gerar dados")
        print("2 - Validar Dados")
        print("0 - Sair")
        print()

        choice = input().strip()

        if choice == "1":
            print("Dados Gerados")
            print()
        elif choice == "2":
            print("Dados validados")
            print()
        elif choice == "0":
            print("Encerre")
            break
        else:
            print("Digite uma das opcoes")
            print()


if __name__ == "__main__":
    main()
