<p align="center">
 📦 <a href="https://pypi.org/project/blockporn" style="text-decoration:none;">BLOCK PORN</a>
</p>


<p align="center">
   <a href="https://telegram.dog/clinton_abraham"><img src="https://img.shields.io/badge/𝑪𝒍𝒊𝒏𝒕𝒐𝒏 𝑨𝒃𝒓𝒂𝒉𝒂𝒎-30302f?style=flat&logo=telegram" alt="telegram badge"/></a>
   <a href="https://telegram.dog/Space_x_bots"><img src="https://img.shields.io/badge/Sᴘᴀᴄᴇ 𝕩 ʙᴏᴛꜱ-30302f?style=flat&logo=telegram" alt="telegram badge"/></a>
   <a href="https://telegram.dog/sources_codes"><img src="https://img.shields.io/badge/Sᴏᴜʀᴄᴇ ᴄᴏᴅᴇꜱ-30302f?style=flat&logo=telegram" alt="telegram badge"/></a>
</p>

## INSTALLATION

```bash
  pip install blockporn
```

## USAGE

```python

from Blockporn import Blocker

url = "https://xxx.com"

resu = Blocker().blocker(url)

print(resu)

```

```python
#======[ ADD MORE SITES ]======

from Blockporn import Blocker

url = "https://xxx.dc"

blok = ["xxx.db", "xxx.dc"]

core = Blocker(block=blok)

resu = core.blocker(url)

print(resu)

```

```python
#======[ CUSTOM BLOCK ]======

from Blockporn import Blocker

url = "https://xxx.me"

blok = ["xxx.me", "xxx.ms"]

core = Blocker(block=blok)

resu = core.blocked(url)

print(resu)

```

```python
#======[ LOAD FILE ]======

from Blockporn import LoadeR
from Blockporn import Blocker

path = "./Home/blocked.txt"

urls = LoadeR.loadfile(path)

url = "https://xxx.com"

core = Blocker(block=urls)

resu = core.blocker(url)

print(resu)


```


[11M+ Domains blocked.txt file](https://telegram.me/WARRIOR_TECHNOLOGY/75)


## LICENSE

The MIT License. Please see [License File](https://github.com/Clinton-Abraham/PORN-X-BLOCKER/blob/V1.0/LICENSE) for more information.
