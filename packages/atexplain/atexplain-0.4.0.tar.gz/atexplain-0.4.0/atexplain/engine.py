import ast
import inspect
import linecache

EXCLUDE_MODULES = {"atexplain"}

def explain(node):
    # import
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name in EXCLUDE_MODULES:
                return
            print(f"📘 import {alias.name}")
            print(f"→ Подключается библиотека '{alias.name}'.\n")

    elif isinstance(node, ast.ImportFrom):
        if node.module in EXCLUDE_MODULES:
            return
        names = ", ".join(a.name for a in node.names)
        print(f"📘 from {node.module} import {names}")
        print(f"→ Импортируются объекты из модуля '{node.module}'.\n")

    elif isinstance(node, ast.Assign):
        targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        print(f"📘 Присваивание")
        print(f"→ Создаётся переменная {', '.join(targets)}.\n")

    elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        func = node.value.func
        if isinstance(func, ast.Name):
            print(f"📘 Вызов функции {func.id}")
            print(f"→ Выполняется функция {func.id}().\n")

    elif isinstance(node, ast.If):
        print("📘 Условие if")
        print("→ Выполняется проверка условия if.\n")

    elif isinstance(node, ast.For):
        print("📘 Цикл for")
        print("→ Запускается цикл for.\n")

    elif isinstance(node, ast.While):
        print("📘 Цикл while")
        print("→ Запускается цикл while.\n")

    elif isinstance(node, ast.FunctionDef):
        print(f"📘 Определение функции {node.name}")
        print(f"→ Создаётся функция {node.name}().\n")

def auto_explain():
    try:
        frame = inspect.stack()[1]
        filename = frame.filename
        source = linecache.getlines(filename)
        tree = ast.parse("".join(source))

        print("👨‍🏫 Объяснение кода:\n")

        for node in tree.body:
            explain(node)

        print("\n💡 Соцсети автора:")
        print("VK: vk.com/club234635039")
        print("TG: t.me/AIPythonTeacher_bot")

    except Exception as e:
        print(f"⚠️ Ошибка автообъяснения: {e}")
