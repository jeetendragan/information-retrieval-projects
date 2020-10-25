def mergeLists(list1, list2):
    finalList = []
    p1 = 0
    p2 = 0
    comparisonCount = 0

    while p1 < len(list1) and p2 < len(list2):
        if list1[p1] < list2[p2]:
            comparisonCount += 1
            p1 += 1
        elif list1[p1] > list2[p2]:
            p2 += 1
            comparisonCount += 2       
        else:
            finalList.append(list1[p1])
            comparisonCount += 2
            p1 += 1
            p2 += 1
    return (finalList, comparisonCount)

if __name__ == "__main__":
    p1 = [1, 2, 4, 5, 7, 9, 15]
    p2 = [3, 4, 6, 9]
    p3 = mergeLists(p1, p2)
    print(p3, ',')