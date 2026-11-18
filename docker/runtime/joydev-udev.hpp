#pragma once

#include <algorithm>
#include <map>
#include <string>
#include <utility>
#include <vector>

namespace wolf::core::docker {

// The hotplug message classifies joydev, but Chromium's cold enumeration reads
// the udev database instead. Keep both views of the same device consistent.
inline auto complete_joydev_udev_entries(
    const std::vector<std::map<std::string, std::string>>& events,
    std::vector<std::pair<std::string, std::vector<std::string>>> entries) {
  const auto decimal = [](const std::string& value) {
    return !value.empty() && std::all_of(value.begin(), value.end(),
                                       [](char c) { return c >= '0' && c <= '9'; });
  };
  for (const auto& event : events) {
    const auto name = event.find("DEVNAME");
    const auto joystick = event.find("ID_INPUT_JOYSTICK");
    const auto major = event.find("MAJOR");
    const auto minor = event.find("MINOR");
    if (name == event.end() || joystick == event.end() || joystick->second != "1" ||
        major == event.end() || minor == event.end() ||
        !name->second.starts_with("/dev/input/js") ||
        !decimal(name->second.substr(13)) ||
        !decimal(major->second) || !decimal(minor->second))
      continue;
    const auto filename = "c" + major->second + ":" + minor->second;
    if (std::any_of(entries.begin(), entries.end(),
                    [&](const auto& entry) { return entry.first == filename; }))
      continue;
    std::vector<std::string> properties{"E:ID_INPUT=1", "E:ID_INPUT_JOYSTICK=1"};
    for (const auto& [key, value] : event) {
      if (key.starts_with("ID_") && key != "ID_INPUT" && key != "ID_INPUT_JOYSTICK")
        properties.push_back("E:" + key + "=" + value);
    }
    entries.emplace_back(filename, std::move(properties));
  }
  return entries;
}

}  // namespace wolf::core::docker
