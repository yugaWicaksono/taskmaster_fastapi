class ListHelper(object):

    @staticmethod
    def find_index_for_id(search_list: list, p_id: int):
        """
        Find index of given element in the list

        :param search_list: the list to be search
        :param p_id: the id of element to be found
        :return: index of the element in the list
        """
        for i in range(len(search_list)):
            if search_list[i]["id"] == p_id:
                return i
        return None

    @staticmethod
    def delete_element(search_list: list, p_id: int) -> list:
        """
        Delete found element in the list

        :param search_list: list to be search
        :param p_id: the id to be found in the list
        :return: list with deleted element or original if element is not found
        """
        index = ListHelper.find_index_for_id(search_list, p_id)
        if index is not None:
            del search_list[index]
        # return original list if not found
        return search_list
