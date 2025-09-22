# DNS OVER HTTPS CLIENT FOR KODI

doh client http based on requests

## script.module.netunblock

Include the script in your addon.xml

```xml
<requires>
    <import addon="script.module.netunblock"/>
</requires>
```

Import doh client and use it

```python
from doh_client import requests
```


## make dns doh server on huggingface

clone repository https://huggingface.co/spaces/zoreu/dohserver

change default url or no in 'Alterar configuração'
