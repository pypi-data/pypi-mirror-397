import random

class MafiaGame:
    def __init__(self):
        self.players = []
        self.roles = {}
        self.alive = set()
        self.round = 0

    def add_players(self):
        print("🎭 Mafiya Oyunu - Realistic CLI")
        n = int(input("Oyuncu sayı (minimum 4): "))
        while n < 4:
            print("❌ Minimum 4 oyunçu olmalıdır.")
            n = int(input("Oyuncu sayı: "))
        for i in range(n):
            name = input(f"{i+1}. Oyuncu adını daxil edin: ").strip()
            self.players.append(name)
        self.alive = set(self.players)
        print("\nOyuncular əlavə edildi!\n")

    def assign_roles(self):
        n = len(self.players)
        num_mafia = max(1, n // 4)
        roles_list = ["Mafiya"] * num_mafia + ["Polis"] + ["Şəhərli"] * (n - num_mafia - 1)
        random.shuffle(roles_list)
        self.roles = dict(zip(self.players, roles_list))
        print("🎲 Rollar təsadüfi paylandı! (Gizli)\n")

    def night_phase(self):
        print("\n🌙 Gecə fazası: Mafiya hərəkət edir")
        mafia_players = [p for p in self.alive if self.roles[p] == "Mafiya"]
        if not mafia_players:
            return None
        target = random.choice([p for p in self.alive if self.roles[p] != "Mafiya"])
        self.alive.remove(target)
        print(f"💀 {target} mafiyalar tərəfindən öldürüldü!")

        # Polis yoxlaması
        police_players = [p for p in self.alive if self.roles[p] == "Polis"]
        if police_players:
            pol = police_players[0]
            suspect = random.choice([p for p in self.alive if p != pol])
            print(f"🕵️ Polis {suspect}-i yoxladı: {self.roles[suspect]}")

    def day_phase(self):
        print("\n🌞 Gündüz fazası: Səsvermə")
        print(f"Canlı oyunçular: {', '.join(self.alive)}")
        if len(self.alive) <= 1:
            return
        vote_out = random.choice(list(self.alive))
        self.alive.remove(vote_out)
        print(f"🔨 Oyuncular {vote_out}-i çıxartdı!")
    
    def check_win(self):
        mafia_alive = [p for p in self.alive if self.roles[p] == "Mafiya"]
        town_alive = [p for p in self.alive if self.roles[p] != "Mafiya"]
        if not mafia_alive:
            print("\n🎉 Şəhər qalib gəldi! Mafiya məğlub oldu.")
            return True
        elif len(mafia_alive) >= len(town_alive):
            print("\n💀 Mafiya qalib gəldi! Şəhər məğlub oldu.")
            return True
        return False

    def play(self):
        self.add_players()
        self.assign_roles()

        while True:
            self.round += 1
            print(f"\n===== Round {self.round} =====")
            self.night_phase()
            if self.check_win():
                break
            self.day_phase()
            if self.check_win():
                break

        print("\n🎭 Oyun bitdi! Rollar belə idi:")
        for p, r in self.roles.items():
            status = "Canlı" if p in self.alive else "Ölü"
            print(f"{p}: {r} ({status})")

def main():
    game = MafiaGame()
    game.play()
