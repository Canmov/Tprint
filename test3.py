numbers = [(2,3), (4, 1)]
sorted_numbers = sorted(numbers[1])
print(sorted_numbers)  # [1, 2, 3, 4]

pairs = [(1, '3'), (2, '1'),(3, '2')]
sorted_pairs = sorted(pairs, key=lambda pair: pair[1])
print(sorted_pairs)  # [(1, 'one'), (3, 'three'), (2, 'two')]
