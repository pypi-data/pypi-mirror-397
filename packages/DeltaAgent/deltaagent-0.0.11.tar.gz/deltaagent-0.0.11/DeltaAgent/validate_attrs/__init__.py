

def validate_attrs(self, req_attrs_ls):

        missing_attrs_ls = []

        for attr in req_attrs_ls:
            if getattr(self, attr) is None:
                missing_attrs_ls.append(attr)
        if len(missing_attrs_ls) > 0:
            raise Exception(f'Please setup the [{", ".join(missing_attrs_ls)}] attribute(s) first!')
        else:
            return True