from collections.abc import MutableMapping
from typing import List, Union
import math

PERTURB_SHIFT = 5


class HashMap(MutableMapping):
    def __init__(self, size: int = 50):
        self.size = size
        # self.buckets = [[] for _ in range(self.size)]
        # print(self.buckets)
        self._indices: List[Union[int, None]] = [None for i in range(size)]
        # Це масив значення якого це порядок входження елемента до HashMap
        # А індекси якого це результат взяття остачі від ділення hash(key)
        #
        self._entries = []

    def _is_rebalance_need(self) -> bool:
        """
        Функція яка має сказати чи потрібне ребалансування
        1. Проблема 70% заповненості
        :return:
        """
        max_items = (len(self._indices) << 1) / 3
        if len(self._entries) > int(max_items):
            return True
        return False

    def _rebalance(self):
        """
        indices =  [None, 1, None, None, None, 0, None, 2]
        entries =  [[-9092791511155847987, 'timmy', 'red'],
                    [-8522787127447073495, 'barry', 'green'],
                    [-6480567542315338377, 'guido', 'blue']]
        :return:
        """
        if not self._is_rebalance_need():
            return

        # tmp = 1
        # self.size = round(self.size + (self.size * math.exp(tmp))/(self.size / 10))
        self.size = self.size * 2
        self._indices: List[Union[int, None]] = [None for i in range(self.size)]
        entries_copy = self._entries.copy()
        for hash_result, key, value in entries_copy:
            index = self._get_index(hash_result)
            self._set_item(hash_result, index, key, value, do_rebalance=False)
        # tmp += 1

    def _get_hash_and_index(self, key):
        hash_result = hash(key)
        index = self._get_index(hash_result)
        return hash_result, index

    def _set_item(self, hash_result, index, key, value, do_rebalance=True):
        #                                      |
        # [None, 1, None, None, None, 0, None, 2, None, None, None, None]
        if self._indices[index] is None:
            self._indices[index] = len(self._entries)
            self._entries.append([hash_result, key, value])
            if do_rebalance:
                self._rebalance()
            return

        write_indices_index = None
        write_entries_index = None
        for i in range(index, len(self._indices)):
            # цю умову ми входимо двічі
            # 1. при запису нового елемента якого раніше не було  self._indices[i] is None
            # 2. при перезапису значення по ключу
            # indices = [None, 1, None, None, None, 0, 3, 4, 5, None, 2, 6, 7]
            entries_index = self._indices[i]
            if entries_index is None:
                write_indices_index = i
                write_entries_index = len(self._entries)
                break
            h, k, v = self._entries[entries_index]
            if h == hash_result and key == k:
                write_indices_index = i
                write_entries_index = entries_index
                break
            elif h == hash_result and key != k:
                continue

        else:
            l = self.size
            if do_rebalance:
                self._rebalance()
            self._indices[l + 1] = len(self._entries)
            self._entries.append([hash_result, key, value])

        if write_indices_index is not None:
            self._indices[write_indices_index] = write_entries_index
            entries_value = [hash_result, key, value]
            if write_entries_index < len(self._entries):
                self._entries[write_entries_index] = entries_value
            else:
                self._entries.append(entries_value)

    def _get_index(self, hash_result):
        perturb = hash_result >> PERTURB_SHIFT
        value = (5 * hash_result) + 1 + perturb
        return value % self.size

    def __iter__(self):
        for h, k, v in self._entries:
            yield k

    def __contains__(self, key):
        hash_result, index = self._get_hash_and_index(key)
        for i in range(index, len(self._indices)):
            entries_index = self._indices[i]
            if not entries_index:
                return False
            h, k, v = self._entries[entries_index]
            if h == hash_result and key == k:
                return True
        return False

    def __setitem__(self, key, value):
        """
        :param key: a
        :param value: 5
        :return:
        """
        hash_result, index = self._get_hash_and_index(key)
        # hash(key) = -4131355768826738049
        # index = 7
        self._set_item(hash_result, index, key, value)

    def __getitem__(self, key):
        """
        indices =  [None, 1, None, None, None, 0, None, 2]
        entries =  [[-9092791511155847987, 'timmy', 'red'],
                    [-8522787127447073495, 'barry', 'green'],
                    [-6480567542315338377, 'guido', 'blue']]
        :param key: a
        :return:
        """
        hash_result = hash(key)
        index = self._get_index(hash_result)
        if self._indices[index] is None:
            raise KeyError(key)

        for i in range(index, self.size):
            entries_index = self._indices[i]
            h, k, v = self._entries[entries_index]
            if h == hash_result and key == k:
                return v

    def __getkey__(self, key):
        hash_result = hash(key)
        index = self._get_index(hash_result)
        if self._indices[index] is None:
            raise KeyError(key)

        for i in range(index, self.size):
            entries_index = self._indices[i]
            h, k, v = self._entries[entries_index]
            if h == hash_result and key == k:
                return k

    def __delitem__(self, key):
        hash_result, index = self._get_hash_and_index(key)
        for i in range(index, len(self._indices)):
            entries_index = self._indices[i]
            if not entries_index:
                raise KeyError(key)
            h, k, v = self._entries[entries_index]
            if h == hash_result and key == k:
                self._indices[i] = None

    def __len__(self):
        return len(self._entries)

    def __eq__(self, other):
        for h, key, value in self._entries:
            # h, k = self.__getkey__(key)
            # print(value)
            # print(other[key])
            # print(key)
            # print(other.__getkey__(key))
            if len(self._entries) != len(other):
                return NotImplemented
            if value == other[key] and key == other.__getkey__(key):
                continue
            return NotImplemented
        return True


# hm1 = HashMap()
# hm2 = HashMap()
# #hm2 = dict(a="a1")
# hm1["a"] = "a1"
# hm1["b"] = "b1"
# # hm1["c"] = "a1"
# hm2["a"] = "a1"
# hm2["b"] = "b1"
# # di = iter(hm1)
# # print(f"Dict key 1 {next(di)}")
# # print(f"Dict key 2 {next(di)}")
# print(hm1 == hm2)


hm = HashMap()
hm["a"] = "a5"
hm["b"] = "b5"
hm["b"] = "b55"
print(hm["a"])
print(hm["b"])
try:
    print(hm["c"])
except KeyError as e:
    print("success raise key error for 'c'")
print(f"Key 'b' in dict {'b' in hm}")


try:
    del hm["c"]
except KeyError as e:
    print("delete 'c' key success")

di = iter(hm)
print(f"Dict key 1 {next(di)}")
print(f"Dict key 2 {next(di)}")

for i in range(1_000):
    hm[i] = i
    print(f"i = {i}")
for i in range(1_000):
    if hm[i] != i:
        raise ValueError("Fuck rebalance")


# indices = [None, 1, None, None, None, 0, None, 2]
# entries = [[-9092791511155847987, 'timmy', 'red'],
#            [-8522787127447073495, 'barry', 'green'],
#            [-6480567542315338377, 'guido', 'blue']]
