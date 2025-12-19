from .words import WORDS
import random


class ChainWordGame:
    def __init__(self):
        self.used_words = []
        self.current_word = random.choice(WORDS)
        self.used_words.append(self.current_word)


    def get_next_word(self, word):
        if word[0].lower() !=  self.current_word[-1].lower():
            return False
        
        if word in self.used_words:
            return False 
        return True 
    
    def play(self):
        print("🎯 Şəhər-Şəhər (Chain Word Game)")
        print(f"Baslangic sozu: {self.current_word}\n")

        while True:
            word = input("Son herfe uygun soz deyin: ").strip().lower()

            if word == "exit":
                print("Oyun dayandirildi!")
                break


            if self.get_next_word(word):
                self.used_words.append(word)
                self.current_word = word 
                print(f"✅ Qəbul edildi! Növbəti söz üçün '{self.current_word[-1]}' hərfi ilə başlayın\n")
            else:
                print(f"❌ Səhv! Söz ya düzgün deyil ya da artıq istifadə olunub\n")


            print("Oyun bitdi! Istifade olunan sozler: ")
            print(" ,".join(self.used_words))


def main():
    ChainWordGame().play()

    