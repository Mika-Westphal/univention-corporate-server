import foo  # noqa
import bar  # noqa
_ = lambda s: s  # noqa: E731


def main():
	print('Boing')
	print(_('Dieser Test ist ok'))
	print(_('Hier lieg auch %d Problem vor') % 0)
	x = 'hier'  # noqa


main()
