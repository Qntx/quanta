

<p align="center">
  <a href="https://qntx.github.io/quanta">
    <img src="./docs/assets/images/logos/quanta.png" alt="Quanta" width="200" height="auto" />
  </a>
</p>

<h1 style="text-align: center;">Σ in innovation, harmony in finance.</h1>



## Development

```bash
git clone https://github.com/Qntx/quanta.git
cd quanta
pip install -r requirements.txt
mike serve
```

## Deployment

```bash
mike delete --all
mike set-default --push latest
mike deploy --push --update-aliases develop latest
```

