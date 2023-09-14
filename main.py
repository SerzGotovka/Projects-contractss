import datetime
import sqlite3

conn = sqlite3.connect('contracts.db')
cursor = conn.cursor()

# Создание таблицы "Projects"
cursor.execute('''CREATE TABLE IF NOT EXISTS Projects (
                project_id INTEGER PRIMARY KEY,
                project_name TEXT NOT NULL,
                creation_date TEXT NOT NULL,
                active_contract_id INTEGER,
                FOREIGN KEY (active_contract_id) REFERENCES Contracts(contract_id) ON DELETE CASCADE)''')

# Создание таблицы "Contracts"
cursor.execute('''CREATE TABLE IF NOT EXISTS Contracts (
                contract_id INTEGER PRIMARY KEY,
                contract_name TEXT NOT NULL,
                creation_date TEXT NOT NULL,
                signing_date TEXT,
                status TEXT NOT NULL,
                project_id INTEGER,
                FOREIGN KEY (project_id) REFERENCES Projects(project_id) ON DELETE CASCADE)''')

conn.commit()


class Contract:
    def __init__(self, contract_name):
        self.contract_name = contract_name
        self.creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.signing_date = None
        self.status = "Черновик"
        self.project = None

    def confirm_contract(self):
        self.status = "Активен"
        self.signing_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def finish_contract(self):
        self.status = "Завершен"

    def add_to_project(self, project):
        if self.status == "Активен" and self not in project.contracts:
            if project.active_contract:
                project.active_contract.finish_contract()
            project.add_contract(self)
            self.project = project

    def __str__(self):
        return f"Договор: {self.contract_name}\nСтатус: {self.status}\nДата создания: {self.creation_date}"


class Project:
    def __init__(self, project_name):
        self.project_name = project_name
        self.creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.contracts = []
        self.active_contract = None

    def add_contract(self, contract):
        if contract not in self.contracts:
            self.contracts.append(contract)
            if contract.status == "Активен":
                self.active_contract = contract

    def finish_project(self):
        self.active_contract = None

    def __str__(self):
        return f"Проект: {self.project_name}\nДата создания: {self.creation_date}\n" \
               f"Количество договоров: {len(self.contracts)}\n"


def create_contract():
    contract_name = input("Введите название договора: ")
    contract = Contract(contract_name)
    cursor.execute("INSERT INTO Contracts (contract_name, creation_date, status, project_id) VALUES (?, ?, ?, ?)",
                   (contract.contract_name, contract.creation_date, contract.status, None))
    conn.commit()

    print("Договор успешно создан.")


def confirm_contract():
    cursor.execute("SELECT * FROM Contracts WHERE status = 'Черновик'")
    contracts_data = cursor.fetchall()

    if len(contracts_data) == 0:
        print("Нет доступных договоров для подтверждения.")
    else:
        print("Доступные договоры для подтверждения:")
        for contract_data in contracts_data:
            contract_id, contract_name, creation_date, signing_date, status, project_id = contract_data
            print(f"ID договора: {contract_id}")
            print(f"Название договора: {contract_name}")
            print(f"Дата создания: {creation_date}")
            print(f"Статус: {status}")
            print("-----------------------")

        contract_id = input("Введите ID договора для подтверждения: ")
        signing_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE Contracts SET status = 'Активен', signing_date = ? WHERE contract_id = ?",
                       (signing_date, contract_id))
        conn.commit()

        print("Договор успешно подтвержден.")


def finish_contract():
    cursor.execute("SELECT * FROM Contracts WHERE status = 'Черновик' OR status = 'Активен'")
    contracts_data = cursor.fetchall()

    if len(contracts_data) == 0:
        print("Нет доступных договоров для завершения.")
    else:
        print("Доступные договоры для завершения:")
        for contract_data in contracts_data:
            contract_id, contract_name, creation_date, signing_date, status, project_id = contract_data
            print(f"ID договора: {contract_id}")

            print(f"Название договора: {contract_name}")
            print(f"Дата создания: {creation_date}")
            print(f"Статус: {status}")
            print("-----------------------")

        contract_id = input("Введите ID договора для завершения: ")
        cursor.execute("UPDATE Contracts SET status = 'Завершен' WHERE contract_id = ?", (contract_id,))
        conn.commit()

        print("Договор успешно завершен.")


def create_project():
    project_name = input("Введите название проекта: ")
    project = Project(project_name)
    cursor.execute("INSERT INTO Projects (project_name, creation_date) VALUES (?, ?)",
                   (project.project_name, project.creation_date))
    conn.commit()

    print("Проект успешно создан.")


def add_contract_to_project():
    cursor.execute("SELECT * FROM Projects")
    projects_data = cursor.fetchall()

    if len(projects_data) == 0:
        print("Нет доступных проектов для добавления договора.")
    else:
        print("Доступные проекты для добавления договора:")
        for project_data in projects_data:
            project_id, project_name, creation_date, _ = project_data
            print(f"ID проекта: {project_id}")
            print(f"Название проекта: {project_name}")
            print(f"Дата создания: {creation_date}")
            print("-----------------------")

        project_id = input("Введите ID проекта для добавления договора: ")
        cursor.execute("SELECT * FROM Contracts WHERE status = 'Активен' AND project_id IS NULL")
        contracts_data = cursor.fetchall()

        if len(contracts_data) == 0:
            print("Нет доступных активных договоров для добавления.")
        else:
            print("Доступные активные договоры для добавления:")
            for contract_data in contracts_data:
                contract_id, contract_name, creation_date, signing_date, status, _ = contract_data
                print(f"ID договора: {contract_id}")
                print(f"Название договора: {contract_name}")
                print(f"Дата создания: {creation_date}")
                print("-----------------------")

            contract_id = input("Введите ID договора для добавления в проект: ")
            cursor.execute("UPDATE Contracts SET project_id = ? WHERE contract_id = ?", (project_id, contract_id))
            conn.commit()

            print("Договор успешно добавлен в проект.")


def finish_project():
    cursor.execute("SELECT * FROM Projects")
    projects_data = cursor.fetchall()

    if len(projects_data) == 0:
        print("Нет доступных проектов для завершения.")
    else:
        print("Доступные проекты для завершения:")
        for project_data in projects_data:
            project_id, project_name, creation_date = project_data
            print(f"ID проекта: {project_id}")
            print(f"Название проекта: {project_name}")
            print(f"Дата создания: {creation_date}")
            print("-----------------------")

        project_id = input("Введите ID проекта для завершения: ")
        cursor.execute("UPDATE Projects SET active_contract_id = NULL WHERE project_id = ?", (project_id,))
        conn.commit()

        print("Проект успешно завершен.")


def main():
    while True:
        print("1. Проект")
        print("2. Договор")
        print("3. Завершить работу с программой")
        choice = input("Выберите пункт: ")

        if choice == "1":
            print("1. Создать проект")
            print("2. Добавить договор в проект")
            print("3. Завершить проект")
            project_choice = input("Выберите действие для проекта: ")

            if project_choice == "1":
                create_project()


            elif project_choice == "2":
                add_contract_to_project()
            elif project_choice == "3":
                finish_project()

        elif choice == "2":
            print("1. Создать договор")
            print("2. Подтвердить договор")
            print("3. Завершить договор")
            contract_choice = input("Выберите действие для договора: ")

            if contract_choice == "1":
                create_contract()
            elif contract_choice == "2":
                confirm_contract()
            elif contract_choice == "3":
                finish_contract()

        elif choice == "3":
            break

        else:
            print("Некорректный выбор. Попробуйте еще раз.")


if __name__ == "__main__":
    main()

conn.close()
