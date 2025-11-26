import turtle

axiom = "F"

rules = {
    "F": "F[+F]F"
}

iterations = 1

length = 150

angle = 25


def generate_lsystem(axiom, rules, iterations):
    current = axiom
    for _ in range(iterations):
        next_seq = ""
        for ch in current:
            next_seq += rules.get(ch, ch)
            current = next_seq
    return current

def draw_lsystem(t, instructions,length, angle):
    stack = []
    for cmd in instructions:
        if cmd =="F":
            t.forward(length)
        elif cmd =="+":
            t.right(angle)
        elif cmd =="-":
            t.left(angle)
        elif cmd =="[":
            stack.append((t.position(), t.heading()))
        elif cmd =="]":
            position, heading = stack.pop()
            t.penup()
            t.goto(position)
            t.setheading(heading)
            t.pendown()

            
def main():
    screen = turtle.Screen()
    screen.bgcolor("white")
    t = turtle.Turtle()
    t.speed(0)
    t.width(5)
    t.left(90)
    t.penup()
    t.goto(0, -200)
    t.pendown()

    instructions = generate_lsystem(axiom, rules, iterations)
    draw_lsystem(t,instructions, length, angle)

    screen.mainloop()

if __name__=="__main__":
    main()
