# Write your code here
import enum
import os.path
import json, random, enum, logging, argparse

ACTIONS = ["add",
           "remove",
           "import",  # load cards from file:
           "export",  # save cards to file:
           "ask",  # for definitions of some random cards
           "exit",  # exit the program,
           "log",  # save log
           "hardest card",  # card with the highest wrong answers
           "reset stats"  # reset statictics about wrong answers
           ]


class CardFields(enum.Enum):
    term = 0
    definition = 1
    stat = 2


class FlashCarder:
    class AnswerStatus(enum.Enum):
        WRONG = 0
        RIGHT_FOR_OTHER = 1
        RIGHT = 2

    class AddStatus(enum.Enum):
        SUCCESS = 0
        FAIL_TERM_EXISTS = 1
        FAIL_DEF_EXISTS = 2

    def __init__(self):
        self.cards = []

    def add(self, term, definition) -> (AddStatus, int):
        """
        Returns status od addition and index of new element in case of successful adding,
        index of conflicting flashcard otherwise
        """
        term_idx = self.find(term)
        def_idx = self.find_def(definition)
        if term_idx != -1:
            return self.AddStatus.FAIL_TERM_EXISTS, term_idx
        elif def_idx != -1:
            return self.AddStatus.FAIL_DEF_EXISTS, def_idx
        else:
            self.cards.append([term, definition, 0])
            return self.AddStatus.SUCCESS, len(self.cards) - 1

    def remove(self, term: str) -> bool:
        idx = self.find(term)
        if idx != -1:
            self.cards.pop(idx)
            return True
        else:
            return False

    def import_(self, fname: str) -> list:
        if not os.path.exists(fname):
            raise FileNotFoundError("File not found.")
        with open(fname, 'r') as f:
            self.cards = json.load(f)
            return self.cards

    def export(self, fname="flashcards.json") -> int:
        with open(fname, 'w') as f:
            json.dump(self.cards, f)
        return len(self.cards)

    def take_cards(self, num: int) -> list:
        """
        Returns num random cards
        """
        res = []
        for i in range(num):
            card_idx = random.randint(0, len(self.cards) - 1)
            res.append(self.cards[card_idx])
        return res

    def check_answer(self, term: str, suggested_def: str) -> (AnswerStatus, int):
        term_idx = self.find(term)
        if term_idx == -1:
            raise AttributeError(f"Flashcard with term {term} not found")
        right_def = self.cards[term_idx][CardFields.definition.value]

        if suggested_def == right_def:
            return self.AnswerStatus.RIGHT, term_idx
        elif self.find_def(suggested_def) != -1:
            self.cards[term_idx][CardFields.stat.value] += 1
            idx = self.find_def(suggested_def)
            return self.AnswerStatus.RIGHT_FOR_OTHER, idx
        else:
            self.cards[term_idx][CardFields.stat.value] += 1
            return self.AnswerStatus.WRONG, -1

    def find(self, term: str) -> int:
        return self.find_by_field(term, CardFields.term)

    def find_def(self, definition: str) -> int:
        return self.find_by_field(definition, CardFields.definition)

    def find_by_field(self, value: str, field: CardFields) -> int:
        for i, card in enumerate(self.cards):
            if card[field.value] == value:
                return i
        return -1

    def len_cards(self):
        return len(self.cards)

    def reset_stat(self):
        for card in self.cards:
            card[CardFields.stat.value] = 0

    def hardest_cards(self) -> (int, list):
        if len(self.cards) == 0:
            return 0, []

        error_counter = [card[CardFields.stat.value] for card in self.cards]
        hardest_num = max(error_counter)
        hardest_idxs = []
        for i, card in enumerate(self.cards):
            if hardest_num == card[CardFields.stat.value]:
                hardest_idxs.append(i)
        return hardest_num, hardest_idxs


STR_NUM_CARDS = "Input the number of cards:"
STR_RECORD = "The {0} for card #{1}:"
STR_RECORD = "The {type}:"
STR_RECORD_ERROR = "The {type} \"{value}\" already exists. Try again:"
STR_ANSWER_CORRECT = "Correct!"
STR_ANSWER_WRONG = "Wrong. The right answer is \"{right}\""
STR_ANSWER_WRONG_HINT = "Wrong. The right answer is \"{right}\", but your definition is correct for \"{other}\"."
STR_ASK = "Print the definition of \"{term}\":"
STR_ASK_ACTION = "\nInput the action "
STR_EXIT = "Bye bye!"

STR_ADD_SUCCESS = "The pair (\"{term}\":\"{definition}\") has been added"
STR_ADD_FAIL = "The {0} \"{1}\" already exists. Try again:"

STR_REMOVE_SUCCESS = "The card has been removed."
STR_REMOVE_FAIL = "Can't remove \"{term}\": there is no such card."

class UserInputHelper:
    log_lines = []

    def __init__(self, flash_carder: FlashCarder, import_file=None, export_file=None):
        self.carder = flash_carder
        self.import_file = import_file
        self.export_file = export_file

        if import_file:
            self.import_cards(import_file)

    def import_cards(self, fname):
        try:
            cards = self.carder.import_(fname)
            if len(cards):
                UserInputHelper.print_(f"{len(cards)} cards have been loaded.")
        except FileNotFoundError:
            UserInputHelper.print_("File not found.")

    def export_cards(self, fname):
        num = self.carder.export(fname)
        if num:
            UserInputHelper.print_(f"{num} cards have been saved.")

    @staticmethod
    def ask_filename():
        return UserInputHelper.input_('File name:\n')

    def process_input(self):
        while True:
            action = UserInputHelper.input_(STR_ASK_ACTION + "(" + ", ".join([act for act in ACTIONS]) + "):\n")
            if action in ACTIONS:
                if action == 'add':
                    self.add_card()

                elif action == 'remove':
                    term = UserInputHelper.input_("Which card?\n")
                    self.remove_card(term)

                elif action == 'import':
                    fname = self.ask_filename()
                    self.import_cards(fname)

                elif action == 'export':
                    fname = self.ask_filename()
                    self.export_cards(fname)

                elif action == 'ask':
                    num = int(input('How many times to ask?'))
                    self.ask_random_cards(num)

                elif action == 'log':
                    fname = self.ask_filename()
                    self.save_log(fname)

                elif action == "hardest card":
                    self.hardest_card()

                elif action == "reset stats":
                    self.carder.reset_stat()
                    UserInputHelper.print_("Card statistics have been reset.")

                elif action == 'exit':
                    UserInputHelper.print_("Bye bye!")
                    if self.export_file:
                        self.export_cards(self.export_file)
                    break
            else:
                UserInputHelper.print_("Cannot recognize the action above. Try again:")

    def add_card(self):
        def repeated_input(type: CardFields,
                           message: str,
                           error_message: str) -> str:
            value = UserInputHelper.input_(message + '\n')
            while self.carder.find_by_field(value, type) != -1:
                value = UserInputHelper.input_(error_message.format(value=value) + '\n')
            return value

        term = repeated_input(CardFields.term,
                              "The card:",
                              "The term \"{value}\" already exists. Try again:")
        definition = repeated_input(CardFields.definition,
                                    "The definition of the card:",
                                    "The definition \"{value}\" already exists. Try again:")
        self.carder.add(term, definition)
        UserInputHelper.print_(f"The pair (\"{term}\":\"{definition}\") has been added")

    def remove_card(self, term):
        if self.carder.remove(term):
            UserInputHelper.print_("The card has been removed.")
        else:
            UserInputHelper.print_(f"Can't remove \"{term}\": there is no such card.")

    def ask_random_cards(self, num):
        cards = self.carder.take_cards(num)

        for card in cards:
            term = card[CardFields.term.value]
            right_answer = card[CardFields.definition.value]
            answer = UserInputHelper.input_(STR_ASK.format(term=term) + '\n')
            status, idx = card_storage.check_answer(term, answer)
            if status == FlashCarder.AnswerStatus.RIGHT:
                UserInputHelper.print_(STR_ANSWER_CORRECT)
            elif status == FlashCarder.AnswerStatus.RIGHT_FOR_OTHER:
                UserInputHelper.print_(f"Wrong. The right answer is \"{right_answer}\", but your definition is correct for \"{self.carder.cards[idx][CardFields.term.value]}\"")
            else:
                UserInputHelper.print_(f"Wrong. The right answer is \"{right_answer}\"")

    def hardest_card(self):
        num, idxs = self.carder.hardest_cards()
        if num == 0:
            UserInputHelper.print_("There are no cards with errors.")
            return

        if len(idxs) == 1:
            card = self.carder.cards[idxs[0]]
            UserInputHelper.print_(f"The hardest card is \"{card[CardFields.term.value]}\". You have {num} errors answering it.")
        else:
            terms = ["\"" + self.carder.cards[idx][CardFields.term.value] + "\"" for idx in idxs]
            terms = ", ".join(terms)
            UserInputHelper.print_(f"The hardest cards are {terms}. You have {num} errors answering them.")

    def save_log(self, fname):
            with open(fname, 'w') as f:
                f.write("\n".join(self.log_lines))
            UserInputHelper.print_("The log has been saved.")

    @staticmethod
    def input_(text):
        UserInputHelper.print_(text)
        x = input()
        UserInputHelper.log_lines.append(x)
        return x

    @staticmethod
    def print_(text):
        UserInputHelper.log_lines.append(text)
        print(text)


if __name__ == "__main__":
    card_storage = FlashCarder()

    parser = argparse.ArgumentParser()
    parser.add_argument("--import_from", type=str)
    parser.add_argument("--export_to", type=str)
    args = parser.parse_args()

    input_helper = UserInputHelper(card_storage, import_file=args.import_from, export_file=args.export_to)
    input_helper.process_input()