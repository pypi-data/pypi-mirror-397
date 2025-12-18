# copium-autopatch

Make deepcopy go brrr.

This depends on [copium](https://github.com/Bobronium/copium) and
automatically calls `copium.patch.enable()` on Python startup.

### Usage

`pip install 'copium[autopatch]'`

`uvx --with 'copium[autopatch]' $executable`

`uv run --with 'copium[autopatch]' $executable`
