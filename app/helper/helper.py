class Calc():
    def rate(total, recycled):
        if total > 0:
            return "{0:.2f}".format(recycled / total * 100, 2)
        return 0

    def myRound(number):
        number = float(number)
        if number > 0:
            return "{0:.2f}".format(number, 2)
        return 0            

class Security():
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])
        return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


class Format():
    def phone(phone):
        phone = phone.replace("-", "")
        phone = ''.join(e for e in phone if e.isalnum())
        result = {}
        result['phone_1'] = phone[0:3]
        result['phone_2'] = phone[3:6]
        result['phone_3'] = phone[6:10]
        result['phone_4'] = phone[10:]
        return result
