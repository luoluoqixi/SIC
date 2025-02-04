import configparser, json, shutil, os, sys
from copy import deepcopy
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPalette, QColor, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QCompleter, QWidget, QSizePolicy, QHBoxLayout, QGraphicsScene

from ConfigClass import Config
from DownloadIcons import DownloadIconsThread, generate_weapons_icons, generate_food_icons, generate_armors_icons
from InputValidation import validateData, validate_test, rev_json, get_upgrades_ids, add_armor_json, add_weapon_json, \
    edit_armor, edit_weapon, validateConfig, random_crafting_requirements, random_crafting_requirements_2
from Option_w import options_window
from Prompt_w import prompt_window
from ShopData import get_raw_data
from files_manage import create_folder, get_main_json, file_to_dict, get_mods_path, get_res, json_to_file, file_to_str, \
    get_langs, get_endianness, get_def_path
import oead
from load_input import Load_Input
from files_manage import clear_json
from Pyqt_gui import Ui_SIC
from Select_file import Select_file
from Readme import readme_window
from sarc_class import Sarc_file

config_file = 'config.ini'
valid_rgb = 'rgb(21, 155, 130)'
invalid_rgb = 'rgb(239, 74, 70)'
BG_COLOR = [47, 49, 54]

def get_keys_values(obj):
    keys = []
    values = []
    for i in obj.keys():
        keys.append(i)
        values.append(obj[i])
    return keys, values


class Window(QMainWindow, Ui_SIC):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.combobox_icon_size = QSize(35, 35)
        self.combobox_icon_size_big = QSize(70, 70)
        self.data = clear_json()
        self.config = 'config.ini'
        self.data_json = file_to_dict('res/res.json')
        self.shops = self.data_json['shops']
        shops_keys, shops_values = get_keys_values(self.shops)
        self.shops_keys = shops_keys
        self.shops_values = shops_values
        self.shops_name = self.data_json['shops_name']
        shops_name_keys, shops_name_values = get_keys_values(self.shops_name)
        self.shops_name_keys = shops_name_keys
        self.shops_name_values = shops_name_values
        self.shops_rev = self.data_json['shops_rev']
        # self.actors = get_res('Actors']
        self.weapons = self.data_json['weapons']
        weapons_keys, weapons_values = get_keys_values(self.weapons)
        self.weapons_keys = weapons_keys
        self.weapons_values = weapons_values
        self.weapons_name = self.data_json['weapons_name']
        weapons_name_keys, weapons_name_values = get_keys_values(self.weapons_name)
        self.weapons_name_keys = weapons_name_keys
        self.weapons_name_values = weapons_name_values
        self.armors = self.data_json['armors']
        self.items = self.data_json['items']
        self.items_rev = self.data_json['items_rev']
        self.magic_types = self.data_json['magic']
        self.effects = self.data_json['Effects']
        self.effects_adv_rev = self.data_json['Effects_adv_rev']
        self.series_types = self.data_json['Series_adv']
        self.sheaths = self.data_json['Sheaths']
        self.armor_profiles = ['', 'ArmorHead', 'ArmorLower', 'ArmorUpper']
        self.wep_profiles = ['', 'WeaponSmallSword', 'WeaponLargeSword', 'WeaponBow', 'WeaponSpear', 'WeaponShield']
        validateConfig(self.config)
        self.langs = get_langs()
        self.options_w = options_window(valid_rgb=valid_rgb, invalid_rgb=invalid_rgb, config_file=config_file)
        self.readme_w = readme_window()
        self.prompt_w = prompt_window(valid_rgb, invalid_rgb, config_file, Style_Sheet=self.styleSheet())
        self.update_config = True
        self.setupUi(self)
        self.setup_ui_local()

    def setup_ui_local(self):
        # hide
        self.korok_mask.hide()
        self.anims.hide()
        # config
        conf = Config()
        config = configparser.ConfigParser()
        config.read(conf.config_file)
        try:
            if config['DEFAULT']['is_bcml_settings'] == "True":
                conf.get_paths()
                conf.save_to_config()
        except:
            config['DEFAULT']['is_bcml_settings'] = "False"
            with open(conf.config_file, 'w') as f:  # save
                config.write(f)
        # windows
        self.prompt_w.frame.setStyleSheet(self.frame.styleSheet())
        # variables
        self.shop_default = [key for key in self.shops.keys()][0]
        # self.item1.setView(QtWidgets.QListView())
        # Buttons
        self.Upgrade_armors.clicked.connect(lambda: validate_test(self))
        self.Add_armors_to_items.clicked.connect(self.add_armors_to_items)
        self.Create_mod.clicked.connect(self.create_mod)
        self.Add_weapon.clicked.connect(self.add_weapon)
        self.Add_armor.clicked.connect(self.add_armor)
        self.Clear_list.clicked.connect(self.clear_list)
        self.Remove_from_mod.clicked.connect(self.remove_from_mod)
        self.Options.clicked.connect(self.options)
        self.patreon.clicked.connect(lambda: os.system(f'start https://docs.qq.com/doc/DWnRGT0ZQR25WZ29w'))
        self.Random_Crafting.clicked.connect(lambda: random_crafting_requirements(self))
        self.Random_Crafting_2.clicked.connect(lambda: random_crafting_requirements_2(self))
        # self.patreon.hide()
        self.edit.clicked.connect(self.edit_click)

        # combo boxes
        self.items_weapons = deepcopy(self.items)
        for a in self.armors:
            del self.items_weapons[a]
        if 'Add' in self.Add_armors_to_items.text():
            self.items = self.items_weapons
        medium_h = 25
        big_h = 30
        self.profile_2.addItems(self.wep_profiles)
        self.profile.addItems(self.armor_profiles)
        self.Lang.addItems(self.langs)
        # self.base_2.addItems(self.weapons)
        for w, item in self.weapons.items():
            icon_tmp = QIcon(os.path.join(r'res\icons', f'{item}.png'))
            self.base_2.addItem(icon_tmp, w)
            self.base_2_name.addItem(icon_tmp, self.weapons_name[w])
        # self.base.addItems(self.armors)
        for a, item in self.armors.items():
            icon_tmp = QIcon(os.path.join(r'res\icons', f'{item}.png'))
            self.base.addItem(icon_tmp, a)
        self.series.addItem("")
        for a, item in self.series_types.items():
            icon_tmp = QIcon(os.path.join(r'res\icons', f'{item}.png'))
            self.series.addItem(icon_tmp, a)

        # self.series.addItems(self.series_types)
        # for item in self.items:
        for key, item in self.items_rev.items():
            if 'Armor' not in item:
                icon_tmp = QIcon(os.path.join(r'res\icons', f'{key}.png'))
                self.item1.addItem(icon_tmp, item)
                self.item2.addItem(icon_tmp, item)
                self.item3.addItem(icon_tmp, item)
                self.item1_2.addItem(icon_tmp, item)
                self.item2_2.addItem(icon_tmp, item)
                self.item3_2.addItem(icon_tmp, item)
        if os.path.exists(r'res\icons'):
            self.series.setIconSize(self.combobox_icon_size_big)
            self.base_2.setIconSize(self.combobox_icon_size_big)
            self.base_2_name.setIconSize(self.combobox_icon_size_big)
            self.effect.setIconSize(self.combobox_icon_size)
            self.base.setIconSize(self.combobox_icon_size_big)
            self.item1.setIconSize(self.combobox_icon_size)
            self.item2.setIconSize(self.combobox_icon_size)
            self.item3.setIconSize(self.combobox_icon_size)
            self.item1_2.setIconSize(self.combobox_icon_size)
            self.item2_2.setIconSize(self.combobox_icon_size)
            self.item3_2.setIconSize(self.combobox_icon_size)

        self.sheath.addItems(self.sheaths)
        self.shop.addItems(self.shops_keys)
        self.shop_name.addItems(self.shops_name_values)

        # self.effect.addItems(self.effects)
        for eff in self.effects:
            icon_tmp = QIcon(os.path.join('res', f'{eff}.png'))
            self.effect.addItem(icon_tmp, eff)
        self.effect.adjustSize()

        self.item1_2.setMaxVisibleItems(medium_h)
        self.item2_2.setMaxVisibleItems(medium_h)
        self.item3_2.setMaxVisibleItems(medium_h)
        self.item1.setMaxVisibleItems(medium_h)
        self.item2.setMaxVisibleItems(medium_h)
        self.item3.setMaxVisibleItems(medium_h)
        self.base_2.setMaxVisibleItems(big_h)
        self.base_2_name.setMaxVisibleItems(big_h)
        self.base.setMaxVisibleItems(big_h)
        self.sheath.setMaxVisibleItems(medium_h)
        self.effect.setMaxVisibleItems(medium_h)
        self.series.setMaxVisibleItems(medium_h)
        self.shop.setMaxVisibleItems(big_h)
        self.shop_name.setMaxVisibleItems(big_h)

        # radio buttons
        if get_endianness():
            self.wiiu_radiobutton.setChecked(True)
        else:
            self.switch_radiobutton.setChecked(True)

        # autocompleters
        # self.base.setCompleter(QCompleter(self.armors))
        self.magic.setCompleter(QCompleter(self.magic_types))
        # self.base_2.setCompleter(QCompleter(self.weapons))

        # menu bar
        self.actionOpen.triggered.connect(self.open_json)
        self.actionQuit.triggered.connect(lambda: self.close())
        self.actionOptions.triggered.connect(self.options)
        self.actionSave.triggered.connect(lambda: json_to_file(os.path.join('jsons', f'{self.pack_name.text()}.json'),
                                                               self.data))
        self.actionSave_as.triggered.connect(self.save_as)
        self.actionReadme.triggered.connect(self.readme)

        # other windows
        self.sel_file = Select_file()
        self.sel_file.setStyleSheet("""    background-color: rgb(47, 49, 54);
            color: rgb(220, 220, 220);
            font: 10pt "Segoe MDL2 Assets";""")

        # rand
        self.check_mode()

        # resizing setFixedSize
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.frame)
        self.centralwidget.setLayout(self.layout)
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(BG_COLOR[0], BG_COLOR[1], BG_COLOR[2]))
        self.setPalette(pal)

    def add_armors_to_items(self):
        if 'Add' in self.Add_armors_to_items.text():
            for a, item in self.armors.items():
                icon_tmp = QIcon(os.path.join(r'res\icons', f'{item}.png'))
                self.item1.addItem(icon_tmp, a)
                self.item2.addItem(icon_tmp, a)
                self.item3.addItem(icon_tmp, a)
            self.Add_armors_to_items.setText('Remove armors to\nitems list')
        elif 'Remove' in self.Add_armors_to_items.text():
            self.item1.clear()
            self.item2.clear()
            self.item3.clear()
            for key, item in self.items_weapons.items():
                icon_tmp = QIcon(os.path.join(r'res\icons', f'{item}.png'))
                self.item1.addItem(icon_tmp, key)
                self.item2.addItem(icon_tmp, key)
                self.item3.addItem(icon_tmp, key)
                self.item1_2.addItem(icon_tmp, key)
                self.item2_2.addItem(icon_tmp, key)
                self.item3_2.addItem(icon_tmp, key)
            self.Add_armors_to_items.setText('Add armors to\nitems list')

    def readme(self):
        self.readme_w.load_txt()
        self.readme_w.show()

    def set_up_effects(self):
        effects_adv = self.data_json['Effects_adv']
        self.effect.addItem('None')
        for elem in effects_adv:
            icon_tmp = QIcon(os.path.join(r'res\icons', f'{elem}.png'))
            self.effect.addItem(icon_tmp, effects_adv[elem])

    def edit_click(self):
        print('edit click')
        try:
            x = self.Mod_content.currentItem().text()
        except:
            print('Error editing item')
            return
        if not x:
            return
        if self.data['Armors'].get(x):
            edit_armor(self, x)
        elif self.data['Weapons'].get(x):
            edit_weapon(self, x)

    def save_as(self):
        file = self.sel_file.saveFileDialog()
        if file: json_to_file(file, self.data)

    def open_json(self):
        file = self.sel_file.openFileNameDialog()
        # file = sg.popup_get_file(message='Choose json file to load', file_types=(('Json', '*.json'),))
        if file:
            try:
                self.data = file_to_dict(file)
            except json.decoder.JSONDecodeError:
                # sg.popup_error(f'Error reading file: {file}')
                return
            self.Mod_content.clear()
            for elem in self.data['Weapons'].keys():
                self.Mod_content.addItem(elem)
            for elem in self.data['Armors'].keys():
                self.Mod_content.addItem(elem)
            self.pack_name.setText(os.path.basename(file[:-5]))
            self.Upgrade_armors.setEnabled(True)
            # print(f'opening {file}')

    def check_mode(self):
        config = configparser.ConfigParser()
        config.read(self.config)
        # print(self.wiiu_radiobutton.isChecked())
        if self.switch_radiobutton.isChecked():
            config['DEFAULT']['mode'] = 'switch'
        elif self.wiiu_radiobutton.isChecked():
            config['DEFAULT']['mode'] = 'wiiu'
        with open(self.config, 'w') as f:
            config.write(f)

    def create_mod(self):
        # print('create_mod function')
        if os.path.exists('cache'):
            shutil.rmtree('cache')
        if not (self.pack_name.text() and self.Lang.currentText() and os.path.exists(self.config)):
            return
        self.check_mode()
        Load_Input(self.data, self.pack_name.text(), self.Lang.currentText(), self.progressBar).create_pack()

    def add_weapon(self):
        # print('add_weapon function')
        base = self.base_2.currentText()
        if base not in self.weapons:
            print(f'Weapon {base} does not exist')
            return
        if not self.name_2.text():
            return
        for elem in [self.item1_2.currentText(), self.item2_2.currentText(), self.item3_2.currentText()]:
            if elem not in self.items:
                return
        if self.name_2.text() in self.data['Weapons'].keys():
            del self.data['Weapons'][self.name_2.text()]
        self.data = add_weapon_json(self, base)
        if not self.Mod_content.findItems(self.name_2.text(), QtCore.Qt.MatchExactly):
            self.Mod_content.addItem(str(self.name_2.text()))

    def add_armor(self):
        # Validation
        base = self.base.currentText()
        if base not in self.armors or not self.name.text():
            print(f'Armor {base} does not exist')
            return
        for elem in [self.item1.currentText(), self.item2.currentText(), self.item3.currentText()]:
            if not elem in self.items:
                return
        shop_local = ''
        armorNextRankName = ''
        armorStarNum = ''
        itemUseIconActorName = ''
        if self.name.text() in self.data['Armors'].keys():
            if self.data['Armors'][self.name.text()].get('armorNextRankName'): armorNextRankName = deepcopy(
                self.data['Armors'][self.name.text()]['armorNextRankName'])
            if self.data['Armors'][self.name.text()].get('armorStarNum'): armorStarNum = deepcopy(
                self.data['Armors'][self.name.text()]['armorStarNum'])
            if self.data['Armors'][self.name.text()].get('itemUseIconActorName'): itemUseIconActorName = deepcopy(
                self.data['Armors'][self.name.text()]['itemUseIconActorName'])
            if self.data['Armors'][self.name.text()].get('shop'):
                if 'Npc_DressFairy' in self.data['Armors'][self.name.text()].get('shop', ''):
                    shop_local = deepcopy(self.data['Armors'][self.name.text()]['shop'])
            else:
                shop_local = self.shops[self.shop.currentText()]
            del self.data['Armors'][self.name.text()]
        else:
            shop_local = self.shops[self.shop.currentText()]
        if not shop_local:
            shop_local = self.shops[self.shop.currentText()]

        self.data = add_armor_json(self, shop_local, base, armorNextRankName, armorStarNum, itemUseIconActorName)
        if not self.Mod_content.findItems(self.name.text(), QtCore.Qt.MatchExactly):
            self.Mod_content.addItem(str(self.name.text()))

    def clear_list(self):
        # print('clear_list function')
        if self.data == clear_json(): return
        self.data = clear_json()
        self.Mod_content.clear()
        self.prompt_w.setWindowTitle('Message')
        self.prompt_w.buttons()
        self.prompt_w.message.setPlainText('Mod content cleared successfully')
        self.Upgrade_armors.setEnabled(True)
        self.prompt_w.setPalette(self.palette())
        self.prompt_w.show()

    def remove_from_mod(self):
        x = self.Mod_content.currentItem().text()
        if x:
            if x in self.data['Armors'].keys():
                del self.data['Armors'][x]
            elif x in self.data['Weapons'].keys():
                del self.data['Weapons'][x]
            row = self.Mod_content.currentRow()
            self.Mod_content.takeItem(row)

    def options(self):
        self.options_w.frame.setStyleSheet(self.frame.styleSheet())
        self.options_w.setPalette(self.palette())
        self.options_w.show()
        self.options_w.load_from_config()


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    win = Window()
    generate_food_icons(win)
    generate_weapons_icons(win)
    generate_armors_icons(win)
    # win.setFixedSize(win.size())
    # win.setFixedSize(win.layout.sizeHint())
    win.show()
    create_folder('jsons')
    create_folder('res')
    create_folder('cache')
    # json_to_file('res\\res.json', res)
    app.exec()


def init():
    # get_main_json()
    create_folder('jsons')
    create_folder('res')
    create_folder('cache')
    if not os.path.exists('config.ini'):
        dump = ''  # sg.popup_get_folder('Please enter a path to BOTW dump')
        if not dump: sys.exit()
        if not os.path.exists(dump):
            # sg.popup_error(f'Path {dump} does not exist')
            sys.exit()
        # sg.popup('Results', 'The value returned from popup_get_folder', text)
        with open('config.ini', 'w') as f:
            f.write(f"""[DEFAULT]
path = {dump}
mods_path = MODS
lang = Bootup_EUen
mode = wiiu""")
    else:
        config = configparser.ConfigParser()
        config.read('config.ini')
        PATH = str(config['DEFAULT']['path'])
        if not os.path.exists(PATH):
            # sg.popup_error(f'Path \n{PATH} \ndoes not exist. Program will now exit')
            sys.exit()


def test():
    try:
        shutil.rmtree('MODS')
    except:
        pass
    create_folder('MODS')
    data = file_to_dict('jsons\\Madara_test.json')
    data, flag = validate_test(data)
    print(data)
    # Load_Input(file_to_json('jsons\\Madara.json'), 'chuchu', 'Bootup_EUen', None).create_pack()
    Load_Input(data, 'TEST', 'Bootup_EUen', None).create_pack()


if __name__ == '__main__':
    # init()
    main()
    # test()
