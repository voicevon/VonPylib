from von.terminal_font import TerminalFont


class Logger():
    style = TerminalFont.Color.Control.reset

    @classmethod
    def Error(cls, title):
        print(TerminalFont.Color.Fore.yellow
            + TerminalFont.Color.Background.red
            + '[Error] ' + title
            + TerminalFont.Color.Control.reset
        )
        cls.style = TerminalFont.Color.Fore.red



    @classmethod
    def Debug(cls, title):
        print( TerminalFont.Color.Fore.yellow      
                + TerminalFont.Color.Background.blue 
                + '[Debug] ' + title 
                + TerminalFont.Color.Control.reset)            

        cls.style = TerminalFont.Color.Fore.purple

    @classmethod
    def Info(cls, title):
        print( TerminalFont.Color.Fore.blue
            + TerminalFont.Color.Background.orange
            + '[Info] ' + title 
            + TerminalFont.Color.Background.black
            + TerminalFont.Color.Fore.yellow)
        cls.style = TerminalFont.Color.Fore.green

    @classmethod
    def Print(cls, key, value):
        print(cls.style , key , '\t=', value)



if __name__ == '__main__':
    Logger.Debug('Debug ')
    Logger.Print('aaa', 1234)
    Logger.Info('Info')
    Logger.Print('aaaaaaaaaaa',  'ddddddddd')
    Logger.Error(" wrong")
    Logger.Print('dddddddd', 'eeeeeeeeee')
        