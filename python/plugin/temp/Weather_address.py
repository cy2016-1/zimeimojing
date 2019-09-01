from package.base import Base       #基本类

class Weather_address( Base ):

    def start(self,data):

        self.data.up_config({"key":"city_cnid",'value':data})


if __name__ == '__main__':

    Weather_address().start("CN101010100")