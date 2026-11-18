#include <runners/joydev-udev.hpp>
#include <cassert>

int main() {
  using namespace wolf::core::docker;
  using Event = std::map<std::string, std::string>;
  using Entries = std::vector<std::pair<std::string, std::vector<std::string>>>;
  const Event js0{{"DEVNAME", "/dev/input/js0"}, {"MAJOR", "13"}, {"MINOR", "0"},
                  {"ID_INPUT_JOYSTICK", "1"}, {"ID_BUS", "usb"}};
  const Event js1{{"DEVNAME", "/dev/input/js1"}, {"MAJOR", "13"}, {"MINOR", "1"},
                  {"ID_INPUT_JOYSTICK", "1"}};
  const Entries upstream{{"c13:67", {"E:ID_INPUT_JOYSTICK=1"}}};
  const Entries expected{{"c13:67", {"E:ID_INPUT_JOYSTICK=1"}},
                         {"c13:0", {"E:ID_INPUT=1", "E:ID_INPUT_JOYSTICK=1", "E:ID_BUS=usb"}},
                         {"c13:1", {"E:ID_INPUT=1", "E:ID_INPUT_JOYSTICK=1"}}};
  assert(complete_joydev_udev_entries({js0, js1}, upstream) == expected);
  assert(complete_joydev_udev_entries({js0, js1, js0}, expected) == expected);
  const Entries existing{{"c13:0", {"E:ID_INPUT_JOYSTICK=1", "E:ID_MODEL=preserved"}}};
  assert(complete_joydev_udev_entries({js0}, existing) == existing);

  for (const auto& field : {"DEVNAME", "MAJOR", "MINOR", "ID_INPUT_JOYSTICK"}) {
    auto missing = js0;
    missing.erase(field);
    assert(complete_joydev_udev_entries({missing}, upstream) == upstream);
  }
  for (const auto& path : {"/dev/input/event3", "/dev/input/js", "/dev/input/js0/../bad",
                           "/other/js0", "/dev/input/js-1"}) {
    auto unrelated = js0;
    unrelated["DEVNAME"] = path;
    assert(complete_joydev_udev_entries({unrelated}, upstream) == upstream);
  }
  auto malformed = js0;
  malformed["MINOR"] = "../bad";
  assert(complete_joydev_udev_entries({malformed}, upstream) == upstream);
  malformed = js0;
  malformed["ID_INPUT_JOYSTICK"] = "0";
  assert(complete_joydev_udev_entries({malformed}, upstream) == upstream);

  // Removal receives the same event metadata and must identify the exact
  // synthesized files, including multiple controllers and a reused minor.
  auto removal = js0;
  removal["ACTION"] = "remove";
  assert(complete_joydev_udev_entries({removal}, upstream) ==
         complete_joydev_udev_entries({js0}, upstream));
}
