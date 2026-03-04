'''
PROJECT 2 - THE PERFECT GUESS

We are going to write a program that generates a random number and asks the user to
guess it.

If the player's guess is higher than the actual number, the program displays "Lower
number please". Similarly, if the user's guess is too Iow, the program prints "higher
number please" When the user guesses the correct number, the Årogram displays the
number of guesses the player used to arrive at the number.
Hint: Use the random module.

'''


import random

var = True

guesses = 0
print("Guess the Number from [1 to 10]")
print("You have total 4 Choices")

Range = range(1, 11)

random_digit = (random.choice(Range))       # Choice is the default keyword


while(var):
    
    guesses += 1            # It count guesses with while loop
     
        
    n = int(input(("Enter your choice: ")))


    if guesses == 4:
        print("You Lost !")
        break 
    
    if random_digit == n:
        print("Congragulations, Your Guess (", random_digit, ")is Perfecet !!. You take" , guesses, "Guesses")
        var=False
        
    elif random_digit < n:
        print("Hint: Try smaller digit, you left", (4 - guesses), "Choices")
        
    elif random_digit > n:
        print("Hint: Try bigger digit, you left", (4 - guesses), "Choices")

 
