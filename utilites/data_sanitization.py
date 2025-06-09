import html

class RecommendationsSanitizer:
    allowed = ("https://i.ytimg.com/", "https://img.youtube.com/", "https://www.youtube.com/", "https://youtu.be/")
    MAXATTEMPTS = 20
    @classmethod
    def set_allowed(cls, new_allowed):
        """seta um novo allowed caso ele seja valido

        Args:
            new_allowed (tuple): a lista de sistes permitidos a ser atualizado.
        """
        if cls.check_allowed(new_allowed):
            cls.allowed = new_allowed
    
    @staticmethod
    def check_allowed(allowed):
        """Verifica se a lista de sites permitidos é o esperado ou um dado malformado

        Args:
            allowed (tuple): a lista de sistes permitidos a ser verificado.

        Returns:
            bool: True se for uma tupla válida, False caso contrário.
        """
        if allowed:
            if isinstance(allowed, tuple):
                return len(allowed) > 0
        return False
    
    @classmethod
    def is_an_allowed_url(cls, url):
        """Verifica se a URL está na lista de domínios permitidos.

        Args:
            url (str): URL a ser verificada.

        Returns:
            bool: True se for uma URL válida, False caso contrário.
        """
        if url is None:
            return False
        if isinstance(url, str):
            return url.startswith(cls.allowed)
        return False

    @staticmethod
    def sanitize_title(title):
        """cria um novo titulo formatando=o para evitar XSS

        Args:
            title (str): string a ser tratada.

        Returns:
            string: o titulo escapado para evitas XSS.
        """
        return html.escape(title) if isinstance(title, str) else None
    @classmethod
    def build_recommendation_entry(cls, entry):
        """cria a estrutura de daods que sera usada no create_dict

        Args:
            entry (dict): dicionario que sera tratado e checado.

        Returns:
            tupla: primeiro indice sendo o titulo e o segundo um dicionario com as informações extras (url e thumb) caso os dados de entry sejam invalido retorna None para ambos.
        """
        title = cls.sanitize_title(entry.get('titulo'))
        thumb = entry.get('thumb')
        url = entry.get('link')
        if title and cls.is_an_allowed_url(url) and cls.is_an_allowed_url(thumb):
            return title, {'url': url, 'thumb': thumb}
        return None, None

    @classmethod
    def create_dict(cls, ytrecommendations_array):
        """cria um dicionario por meio de um array com estrutura [{titulos: '', thumb: '', link:''}] e trata valores indevidos

        Args:
            ytrecommendations_array(array): a lista de recomendações que precisa ser tratadas.

        Returns:
            dict: retorna um dicionario com a estrutura {titulo_real_do_video: {url: 'youtube.com/', thumb: 'i.ytimg.com'}}.
        """
        if isinstance(ytrecommendations_array, list) and len(ytrecommendations_array) > 0:
            try:
                limit = cls.MAXATTEMPTS
                ytrecommendations = {}
                for i in ytrecommendations_array:
                    if limit == 0:
                        break
                    title, data = cls.build_recommendation_entry(i)
                    if title and data:
                        ytrecommendations[title] = data
                    limit -= 1
                return ytrecommendations
            except Exception as e:
                return {}
        else:
            return {}
        
