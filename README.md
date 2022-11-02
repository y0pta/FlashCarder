### Flash card game
---
When learning a new language, it can be hard to remember all the new vocabulary, which is exactly where flashcards can help. Typically, flashcards show a hint (a task or a picture) on one side and the right answer on the other. Flashcards can be used to remember any sort of data. 
The program uses standard console input and output to interact with user. Cards could be loaded from file or insert by customer. Once cards are inserted, user will be asked a meaning of a card one by one. Number of wrong answers will be saving
during the session and could be restored from file.
### Use command line arguments
---
```sh
> python flashcards.py --import_from file_i --export_to file_e
```
**import_from** - use this option to import cards from file  
**export_to**- use this option for saving flashcards, which filled during the session.
### Script actions
---
After running the script, you will be asked action to perform:
* **"add"** - add card term and appropriate definition
* **"remove"** - delete card with given term
* **"import"**  - load cards from file
* **"export"**  - save cards to file
* **"ask"**  - ask definitions of some random terms sequentially 
* **"exit"**  - exit the program
* **"log"** - save log to the given file 
* **"hardest card"** - print the card with the maximum number of wrong answers
* **"reset stats"** - reset statictics 

