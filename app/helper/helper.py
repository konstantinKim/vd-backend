class Calc():
    def rate(total, recycled):
        if total > 0:
            return "{0:.2f}".format(recycled / total * 100, 2)
        return 0    

class Security():
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])
        return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

