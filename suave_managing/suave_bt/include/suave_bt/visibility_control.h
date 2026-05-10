// Copyright 2024 Gustavo Rezende Silva
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#ifndef SUAVE_BT__VISIBILITY_CONTROL_H_
#define SUAVE_BT__VISIBILITY_CONTROL_H_

// This logic was borrowed (then namespaced) from the examples on the gcc wiki:
//     https://gcc.gnu.org/wiki/Visibility

#if defined _WIN32 || defined __CYGWIN__
  #ifdef __GNUC__
    #define SUAVE_BT_EXPORT __attribute__ ((dllexport))
    #define SUAVE_BT_IMPORT __attribute__ ((dllimport))
  #else
    #define SUAVE_BT_EXPORT __declspec(dllexport)
    #define SUAVE_BT_IMPORT __declspec(dllimport)
  #endif
  #ifdef SUAVE_BT_BUILDING_LIBRARY
    #define SUAVE_BT_PUBLIC SUAVE_BT_EXPORT
  #else
    #define SUAVE_BT_PUBLIC SUAVE_BT_IMPORT
  #endif
  #define SUAVE_BT_PUBLIC_TYPE SUAVE_BT_PUBLIC
  #define SUAVE_BT_LOCAL
#else
  #define SUAVE_BT_EXPORT __attribute__ ((visibility("default")))
  #define SUAVE_BT_IMPORT
  #if __GNUC__ >= 4
    #define SUAVE_BT_PUBLIC __attribute__ ((visibility("default")))
    #define SUAVE_BT_LOCAL  __attribute__ ((visibility("hidden")))
  #else
    #define SUAVE_BT_PUBLIC
    #define SUAVE_BT_LOCAL
  #endif
  #define SUAVE_BT_PUBLIC_TYPE
#endif

#endif  // SUAVE_BT__VISIBILITY_CONTROL_H_
