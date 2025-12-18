def cool_number(n):
    try:
        n = float(n)
    except ValueError:
        return False
    if n < 0:
        n = n * -1
    if n % 1 == 0:
        n = int(n)
    if len(str(n)) == 1:
        return False
    numbers = []
    for i in str(n):
        if i != '.':
            numbers.append(int(i))
    if (0 not in numbers) and len(numbers) != 2:
        temp = numbers[0] - numbers[1]
        flag = True
        for i in range(1, len(numbers)-1):
            if not (numbers[i] - numbers[i+1] == temp):
                flag = False
        if flag:
            return True

        temp = numbers[0] / numbers[1] 
        flag = True
        for i in range(1, len(numbers)-1):
            if not (numbers[i] / numbers[i+1] == temp):
                flag = False
        if flag:
            return True
    
    if numbers == numbers[::-1]:
        return True

    if (n**0.5) % 1 == 0:
        return True
    
    return False

def test1():
    assert (cool_number(1) == False)
    print("Test 1 complete")
    test2()
        
def test2():
    assert cool_number(135)
    print("Test 2 complete")
    test3()
        
def test3():
    assert cool_number(248)
    print("Test 3 complete")
    test4()
        
def test4():
    assert cool_number(1111)
    print("Test 4 complete")
    test5()

def test5():
    assert cool_number(-12.4)
    print("Test 5 complete")
    
