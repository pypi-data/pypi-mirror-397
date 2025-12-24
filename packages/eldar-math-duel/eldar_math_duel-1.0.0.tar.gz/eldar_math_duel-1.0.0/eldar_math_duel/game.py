import random
import time


class MathDuel:
    def __init__(self):
        self.players = {}
        self.rounds = 5

    def add_players(self):
        print("⚔️ Riyaziyyat Dueli")
        p1 = input("1-ci oyunçunun adı: ").strip()
        p2 = input("2-ci oyunçunun adı: ").strip()

        self.players[p1] = 0
        self.players[p2] = 0

    def generate_question(self):
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        op = random.choice(["+", "-", "*"])
        question = f"{a} {op} {b}"
        return question, eval(question)

    def ask(self, player):
        q, ans = self.generate_question()
        print(f"\n{player}: {q} = ?")
        start = time.time()
        user = input("Cavab (exit): ").strip()

        if user.lower() == "exit":
            return "exit"

        try:
            if int(user) == ans:
                self.players[player] += 1
                print("✅ Düzdür!")
            else:
                print(f"❌ Səhv! Düz cavab: {ans}")
        except:
            print("❌ Yanlış format!")

        print(f"⏱️ Vaxt: {round(time.time()-start,2)} s")

    def play(self):
        self.add_players()
        names = list(self.players.keys())

        for r in range(1, self.rounds + 1):
            print(f"\n🔁 Raund {r}")
            for p in names:
                if self.ask(p) == "exit":
                    self.result()
                    return

        self.result()

    def result(self):
        print("\n🏁 Nəticə:")
        for p, s in self.players.items():
            print(f"{p}: {s} xal")


def main():
    MathDuel().play()
