#!/usr/bin/env python3
"""
Patch IL2CPP generated C++ files for Ori and the Blind Forest DE on iOS:
1. Fix OutputFolder.AppData and OutputFolder.BuildOutputPath (Assembly-CSharp__14.cpp)
   to use Application.persistentDataPath instead of Directory.GetCurrentDirectory() ("/")
   or Application.dataPath (read-only .app/Data bundle), fixing the fatal
   UnauthorizedAccessException: Access to the path '/Ori and the Blind Forest DE Trial' is denied
   inside GameController.Awake() -> HandleTrialData().
2. Fix FPSTestOutput..ctor (Assembly-CSharp__8.cpp) to use Application.persistentDataPath.
3. Stub WindowManager user32.dll P/Invokes and WindowManager.Update (Assembly-CSharp__28.cpp)
   to eliminate 5x/sec DllNotFoundException: user32.dll spam.
4. Stub XInput P/Invokes (xinput9_1_0.dll) and XboxController polling thread
   (J2i.Net.XInputWrapper.cpp & Assembly-CSharp__29.cpp).
5. Stub HighPerformanceCounter Kernel32.dll P/Invokes (Assembly-CSharp__9.cpp).
6. Stub AVProWindowsMediaPlugin.Init P/Invoke (Assembly-CSharp__1.cpp) to return false cleanly.
"""

import os
import re
import sys


def replace_func_body(content: str, func_decl_prefix: str, new_body: str) -> str:
    """Find a C++ function definition (NOT forward declaration) by its prefix and replace its `{ ... }` body."""
    pattern = re.compile(re.escape(func_decl_prefix) + r"(?:\s*\([^;{}]*\))?\s*\{")
    m = pattern.search(content)
    if not m:
        raise RuntimeError(f"Function definition not found: {func_decl_prefix}")
    brace_start = m.end() - 1
    depth = 0
    for i in range(brace_start, len(content)):
        c = content[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                brace_end = i
                return content[:brace_start] + "{\n" + new_body + "\n}" + content[brace_end + 1 :]
    raise RuntimeError(f"Closing brace not found for: {func_decl_prefix}")


def patch_assembly_csharp_14(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__14.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    extern_decl = (
        "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* "
        "Application_get_persistentDataPath_mC58BD3E1A20732E0A536491DBCAE6505B1624399 (const RuntimeMethod* method);\n"
    )
    target_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* OutputFolder_get_AppData_mAE64D001E495438B43CE5C2EDF5DB4A8F67516CB"

    if "Application_get_persistentDataPath_mC58BD3E1A20732E0A536491DBCAE6505B1624399" not in content:
        content = content.replace(target_decl, extern_decl + target_decl, 1)

    appdata_body = """\tstatic bool s_Il2CppMethodInitialized;
\tif (!s_Il2CppMethodInitialized)
\t{
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Application_tDB03BE91CDF0ACA614A5E0B67CFB77C44EB19B21_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&String_t_il2cpp_TypeInfo_var);
\t\ts_Il2CppMethodInitialized = true;
\t}
\t{
\t\til2cpp_codegen_runtime_class_init_inline(OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_il2cpp_TypeInfo_var);
\t\tString_t* L_0 = ((OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_StaticFields*)il2cpp_codegen_static_fields_for(OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_il2cpp_TypeInfo_var))->___m_appData;
\t\tString_t* L_1 = ((String_t_StaticFields*)il2cpp_codegen_static_fields_for(String_t_il2cpp_TypeInfo_var))->___Empty;
\t\tbool L_2 = String_op_Equality_m030E1B219352228970A076136E455C4E568C02C1(L_0, L_1, NULL);
\t\tif (L_2 || !L_0)
\t\t{
\t\t\til2cpp_codegen_runtime_class_init_inline(Application_tDB03BE91CDF0ACA614A5E0B67CFB77C44EB19B21_il2cpp_TypeInfo_var);
\t\t\tString_t* L_3 = Application_get_persistentDataPath_mC58BD3E1A20732E0A536491DBCAE6505B1624399(NULL);
\t\t\t((OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_StaticFields*)il2cpp_codegen_static_fields_for(OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_il2cpp_TypeInfo_var))->___m_appData = L_3;
\t\t\tIl2CppCodeGenWriteBarrier((void**)(&((OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_StaticFields*)il2cpp_codegen_static_fields_for(OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_il2cpp_TypeInfo_var))->___m_appData), (void*)L_3);
\t\t}
\t\treturn ((OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_StaticFields*)il2cpp_codegen_static_fields_for(OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_il2cpp_TypeInfo_var))->___m_appData;
\t}"""

    content = replace_func_body(content, target_decl, appdata_body)

    # Also patch OutputFolder_get_BuildOutputPath to use persistentDataPath instead of dataPath
    build_output_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* OutputFolder_get_BuildOutputPath_m1295B72AD4610F7F4E48ADF6DF473A3FBA3FBD6E"
    build_output_body = """\tstatic bool s_Il2CppMethodInitialized;
\tif (!s_Il2CppMethodInitialized)
\t{
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Application_tDB03BE91CDF0ACA614A5E0B67CFB77C44EB19B21_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Path_t8A38A801D0219E8209C1B1D90D82D4D755D998BC_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral71443AC7CF5CC108984A138188DE915E32441BB2);
\t\ts_Il2CppMethodInitialized = true;
\t}
\t{
\t\til2cpp_codegen_runtime_class_init_inline(OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_il2cpp_TypeInfo_var);
\t\tString_t* L_0 = ((OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_StaticFields*)il2cpp_codegen_static_fields_for(OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_il2cpp_TypeInfo_var))->___m_path;
\t\tif (L_0)
\t\t{
\t\t\tgoto IL_0032;
\t\t}
\t}
\t{
\t\til2cpp_codegen_runtime_class_init_inline(Application_tDB03BE91CDF0ACA614A5E0B67CFB77C44EB19B21_il2cpp_TypeInfo_var);
\t\tString_t* L_1;
\t\tL_1 = Application_get_persistentDataPath_mC58BD3E1A20732E0A536491DBCAE6505B1624399(NULL);
\t\til2cpp_codegen_runtime_class_init_inline(Path_t8A38A801D0219E8209C1B1D90D82D4D755D998BC_il2cpp_TypeInfo_var);
\t\tString_t* L_2;
\t\tL_2 = Path_Combine_m1ADAC05CDA2D1D61B172DF65A81E86592696BEAE(L_1, _stringLiteral71443AC7CF5CC108984A138188DE915E32441BB2, NULL);
\t\til2cpp_codegen_runtime_class_init_inline(OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_il2cpp_TypeInfo_var);
\t\t((OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_StaticFields*)il2cpp_codegen_static_fields_for(OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_il2cpp_TypeInfo_var))->___m_path = L_2;
\t\tIl2CppCodeGenWriteBarrier((void**)(&((OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_StaticFields*)il2cpp_codegen_static_fields_for(OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_il2cpp_TypeInfo_var))->___m_path), (void*)L_2);
\t\tString_t* L_3 = ((OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_StaticFields*)il2cpp_codegen_static_fields_for(OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_il2cpp_TypeInfo_var))->___m_path;
\t\tbool L_4;
\t\tL_4 = Directory_Exists_m3D125E9E88C291CF11113444F961A64DD83AE1C7(L_3, NULL);
\t\tif (L_4)
\t\t{
\t\t\tgoto IL_0032;
\t\t}
\t}
\t{
\t\til2cpp_codegen_runtime_class_init_inline(OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_il2cpp_TypeInfo_var);
\t\tString_t* L_5 = ((OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_StaticFields*)il2cpp_codegen_static_fields_for(OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_il2cpp_TypeInfo_var))->___m_path;
\t\tDirectoryInfo_tEAEEC018EB49B4A71907FFEAFE935FAA8F9C1FE2* L_6;
\t\tL_6 = Directory_CreateDirectory_m16EC5CE8561A997C6635E06DC24C77590F29D94F(L_5, NULL);
\t}

IL_0032:
\t{
\t\til2cpp_codegen_runtime_class_init_inline(OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_il2cpp_TypeInfo_var);
\t\tString_t* L_7 = ((OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_StaticFields*)il2cpp_codegen_static_fields_for(OutputFolder_t38E39FB6EB4C3AE432AF0C27309ACF5B601CF99F_il2cpp_TypeInfo_var))->___m_path;
\t\treturn L_7;
\t}"""

    content = replace_func_body(content, build_output_decl, build_output_body)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__14.cpp (OutputFolder.AppData & BuildOutputPath)")


def patch_assembly_csharp_8(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__8.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    extern_decl = (
        "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* "
        "Application_get_persistentDataPath_mC58BD3E1A20732E0A536491DBCAE6505B1624399 (const RuntimeMethod* method);\n"
    )
    target_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void FPSTestOutput__ctor_mCF76EB1DAB02836CB1F9B3188F8F193226A5AEF3"

    if "Application_get_persistentDataPath_mC58BD3E1A20732E0A536491DBCAE6505B1624399" not in content:
        content = content.replace(target_decl, extern_decl + target_decl, 1)

    content = content.replace(
        "L_7 = Application_get_dataPath_m4C8412CBEE4EAAAB6711CC9BEFFA73CEE5BDBEF7(NULL);",
        "L_7 = Application_get_persistentDataPath_mC58BD3E1A20732E0A536491DBCAE6505B1624399(NULL);",
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__8.cpp (FPSTestOutput..ctor)")


def patch_assembly_csharp_28(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__28.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    stubs = [
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int32_t WindowManager_SetWindowLong_mCFD5DA3B026E0B7248C32D0205BA6FD8341D4A77", "\treturn 0;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int32_t WindowManager_GetWindowLong_m198699DC8E5F16477886FA111A542D726065E61C", "\treturn 0;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR intptr_t WindowManager_FindWindowByCaption_m0312358B79BA2D656C10A9BDF7BB4B04B1AC4647", "\treturn (intptr_t)0;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool WindowManager_DrawMenuBar_mF72298077F088D0584445E53AEA4B357527122F3", "\treturn true;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR intptr_t WindowManager_SetWindowPos_mB73110753A86CB2BD5C2330DC738A4D660393557", "\treturn (intptr_t)0;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool WindowManager_GetWindowRect_mC20188DC8BFD71FC8ABD7F4F0F2A05149C68ABF5", "\treturn false;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR intptr_t WindowManager_GetForegroundWindow_m04C39A2B9AC1AF249B3352C0A9E9B5BF55AFF429", "\treturn (intptr_t)0;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR intptr_t WindowManager_GetActiveWindow_mDD8F8A7F364857589327505783A8761203C4DB00", "\treturn (intptr_t)0;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool WindowManager_ShowWindow_mD25F810979DFD7EF18E5A35FD7D68B0964492231", "\treturn true;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR intptr_t WindowManager_GetFocus_mA6EC78F35AC1053D07CB1BFF9CABD9A13279F9E7", "\treturn (intptr_t)0;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool WindowManager_IsMinimized_mAFE2EE99C3F4B07061FFF0DD55D15D2E6B4EAD7D", "\treturn false;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool WindowManager_HasFocus_mDD4A60387885F086403470E0640CFDE7F962F2F6", "\treturn true;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void WindowManager_Update_m427C31E7534E59600251DCBB5F9FA7252808FDE8", "\treturn;"),
    ]

    for decl, body in stubs:
        content = replace_func_body(content, decl, body)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__28.cpp (WindowManager user32.dll stubs)")


def patch_xinput(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "J2i.Net.XInputWrapper.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1167 = ERROR_DEVICE_NOT_CONNECTED (0x48F)
    stubs = [
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void XboxController_StartPolling_mEE5826257F458F7AAAEE31AD699FF80C77FEFABD", "\treturn;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void XboxController_StopPolling_m3FAAAE574A3CAD7615F87086C61A3E7E3CE8F0D0", "\treturn;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int32_t XInput_XInputGetState_m211ABDFADF57D994D5D0088BB3AB59C39B233055", "\treturn 1167;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int32_t XInput_XInputSetState_mFD41B467DD92AC77ABE7C29139515B4C4D1DB62C", "\treturn 1167;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int32_t XInput_XInputGetCapabilities_m4F9AC6356EF25B7351F4466CF4E288A4D4D85C90", "\treturn 1167;"),
    ]

    for decl, body in stubs:
        content = replace_func_body(content, decl, body)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched J2i.Net.XInputWrapper.cpp (xinput9_1_0.dll stubs)")


def patch_assembly_csharp_9(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__9.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    stubs = [
        (
            "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool HighPerformanceCounter_QueryPerformanceCounter_m47ED2FFF04ED8D40B91EF58BAB48B5C10060E10F",
            "\tif (___0_lpPerformanceCount) *___0_lpPerformanceCount = 0;\n\treturn true;",
        ),
        (
            "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool HighPerformanceCounter_QueryPerformanceFrequency_mDF547280BF854A42E58CFE1267653AFB264A00A6",
            "\tif (___0_lpFrequency) *___0_lpFrequency = 1000000;\n\treturn true;",
        ),
    ]

    for decl, body in stubs:
        content = replace_func_body(content, decl, body)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__9.cpp (Kernel32.dll HighPerformanceCounter stubs)")


def patch_assembly_csharp_1(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__1.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Stub all AVProWindowsMediaPlugin P/Invoke methods so they never attempt to load AVProWindowsMedia.dll
    avpro_pattern = re.compile(
        r"(IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR\s+([a-zA-Z0-9_*]+)\s+AVProWindowsMediaPlugin_[A-Za-z0-9_]+\s*\([^)]*\))\s*\{",
    )

    pos = 0
    count = 0
    while True:
        m = avpro_pattern.search(content, pos)
        if not m:
            break
        decl_prefix = m.group(1)
        ret_type = m.group(2).strip()
        if ret_type == "void":
            body = "\treturn;"
        elif ret_type == "bool":
            body = "\treturn false;"
        elif ret_type == "float":
            body = "\treturn 0.0f;"
        else:
            body = f"\treturn ({ret_type})0;"
        content = replace_func_body(content, decl_prefix, body)
        pos = m.start() + len(decl_prefix) + len(body) + 4
        count += 1

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Patched Assembly-CSharp__1.cpp ({count} AVProWindowsMediaPlugin stubs)")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 patch_il2cpp_ios.py <path_to_xcode_project_dir>")
        sys.exit(1)

    xcode_dir = sys.argv[1]
    cpp_dir = os.path.join(xcode_dir, "Il2CppOutputProject", "Source", "il2cppOutput")
    if not os.path.isdir(cpp_dir):
        print(f"ERROR: il2cppOutput directory not found at: {cpp_dir}")
        sys.exit(1)

    print(f"Applying iOS IL2CPP runtime patches in: {cpp_dir}")
    patch_assembly_csharp_14(cpp_dir)
    patch_assembly_csharp_8(cpp_dir)
    patch_assembly_csharp_28(cpp_dir)
    patch_xinput(cpp_dir)
    patch_assembly_csharp_9(cpp_dir)
    patch_assembly_csharp_1(cpp_dir)
    print("All iOS IL2CPP runtime patches applied successfully!")


if __name__ == "__main__":
    main()
