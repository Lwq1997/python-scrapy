# -*- coding: utf-8 -*-
# @Time    : 2019/4/24 21:53
# @Author  : Lwq
# @File    : depth_tree.py
# @Software: PyCharm
"""
深度优先遍历
"""


def depth_tree(tree_node):
    if tree_node is not None:
        print(tree_node._data)
        if tree_node._left is not None:
            depth_tree(tree_node._left)
        if tree_node._right is not None:
            depth_tree(tree_node._right)

def level_tree(root):
    if root is None:
        return
    my_queue = []
    node = root
    my_queue.append(node)
    while my_queue:
        node = my_queue.pop(0)
        print(node._data)
        if node._left is not None:
            my_queue.append(node._left)
        if node._right is not None:
            my_queue.append(node._right)

class Tree:
    def __init__(self, data, left, right):
        self._data = data
        self._left = left
        self._right = right


root = Tree('a', Tree('b', Tree('d', None, None), Tree('e', None, Tree('i', None, None))),
            Tree('c', Tree('f', None, None), Tree('g', Tree('h', None, None), None)))

root = Tree(1, Tree(2, Tree(4, None, None), Tree(5, None, None)), Tree(3, Tree(6, None, None), Tree(7, None, None)))
depth_tree(root)
print('-'*20)
level_tree(root)
