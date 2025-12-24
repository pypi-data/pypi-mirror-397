import atexit

_asked = False

def ask_explanation():
    global _asked
    if _asked:
        return
    _asked = True

    answer = input("Нужно объяснение работы кода? (да/нет): ").strip().lower()
    if answer == "да":
        print("\n📘 Объяснение:")
        print("1. Код был выполнен построчно.")
        print("2. Все функции и инструкции отработали.")
        print("3. Это автоматическое объяснение от atexplain.\n")
    else:
        print("❌ Объяснение пропущено.")

atexit.register(ask_explanation)
