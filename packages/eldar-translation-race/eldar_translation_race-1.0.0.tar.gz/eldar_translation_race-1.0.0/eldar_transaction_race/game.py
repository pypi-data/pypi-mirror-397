from.words import WORDS
import random

class TranslationRace:
    def __init__(self):
        self.words = WORDS
        self.score = 0
        self.rounds = 0
        self.max_rounds = 5

    def play(self):
        print("🌍 Tərcümə Yarışı (Translation Race)")
        print("İngiliscə söz verilir, Azərbaycan dilinə tərcümə et")
        print("Çıxmaq üçün 'exit' yaz\n")

        word_list = list(self.words.keys())
        random.shuffle(word_list)

        for word in word_list[:self.max_rounds]:
            self.rounds += 1
            answer = input(f"{self.rounds}. '{word}' sözünün Azərbaycan dilində qarşılığı: ").strip().lower()

            if answer == "exit":
                print("\nOyun dayandirildi!")
                break 

            if answer == self.words[word].lower():
                self.score += 1
                print("✅ True!\n")
            else:
                print(f"❌ Səhv! Düzgün cavab: '{self.words[word]}'\n")
        
        print(f"🎉 Oyun bitdi! Toplam xal: {self.score}/{self.rounds}")

def main():
    game = TranslationRace()
    game.play()
