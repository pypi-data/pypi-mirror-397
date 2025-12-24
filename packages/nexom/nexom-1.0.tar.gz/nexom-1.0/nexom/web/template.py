import os, re

from ..core.error import TemplateNotFoundError, TemplatesInvalidTypeError, TemplateKeyNotSetError

class Template:
    def __init__(self, template:str, base_dir:str=..., **kwargs:str):
        if base_dir is Ellipsis :
            base_dir = None

        self.template = template
        self.kwargs = kwargs
        self.base_dir = base_dir

        self._doc = self._assembly()

    def _open(self, template, **kwargs):
        try:
            template_ = template
            if not template_.endswith(".html"):
                template_ += ".html"

            document_path = os.path.join(self.base_dir, template_) if self.base_dir else self.template

            with open(document_path, "r", encoding="utf-8") as d:
                doc = d.read()

            return self._render(doc, **kwargs)
        except FileNotFoundError:
            raise TemplateNotFoundError(template)
        except Exception as e:
            raise e

    def _render(self, doc, **kwargs) -> str:
        tp = re.compile(r"\{\{\s*(\w+)\s*\}\}")
        
        def replace(m):
            key = m.group(1)
            if key not in kwargs:
                raise TemplateNotFoundError(key)
            return str(kwargs[key])

        return tp.sub(replace, doc)

    def _assembly(self):
        doc = self._open(self.template, **self.kwargs)

        em = re.search(r"<Extends\s+([\w\.]+)\s*/>", doc)
        if em:
            extends_doc = em.group(1)

            im = re.findall(r"<Insert\s+([\w\.]+)>(.*?)</Insert>", doc, flags=re.DOTALL)
            format_values = self.kwargs
            for target, content in im:
                format_values[target] = content.strip()
            
            doc = self._open(extends_doc, **format_values)

        mp = re.compile(r"<Import\s+(\w+)\s*/>")
        def replace(m):
            template = m.group(1)
            m_doc = self._open(template)
            return m_doc

        return mp.sub(replace, doc)


    def __repr__(self) -> str:
        return self._doc
    def __str__(self) -> str:
        return self.__repr__()

    def push(self, **kwargs:str) -> str:
        self.kwargs = kwargs
        self._open()
        return self.__repr__()

class Templates:
    def __init__(self, base_dir:str, *templates:str):
        self.base_dir = base_dir

        for template in templates:
            
            self.append(template)

    def append(self, template:str) -> None:
        t = template.removesuffix(".html")
        def _call(**kwargs:str) -> str:
            return Template(t, self.base_dir, **kwargs).__repr__()
        setattr(self, template, _call)

    def delete(self, template:str) -> None:
        if hasattr(self, template):
            delattr(self, template)
