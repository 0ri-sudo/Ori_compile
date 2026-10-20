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
   (J2i.Net.XInputWrapper.cpp).
5. Stub HighPerformanceCounter Kernel32.dll P/Invokes (Assembly-CSharp__9.cpp).
6. Stub AVProWindowsMediaPlugin P/Invoke methods and clamp _DepthFlipScreen.x in
   AtlasSpriteTextureBinder.BindTo (Assembly-CSharp__1.cpp) for Metal Reversed-Z.
7. Guard MenuScreenManager.Instantiate and Setup* methods against null prefabs on
   the title screen (Assembly-CSharp__11.cpp) so MenuScreenManager.Awake() completes.
8. Wire OriPortShaderFallback + UpdateAlphaGrab + RenderUserInterface into
   OriPortManualPresenter.RenderFrame, disable Hidden/EarlyZWrite dummy renderers,
   clamp _DepthFlipScreen.x, and enable OriPortTouchControls on the title screen
   (Assembly-CSharp__13.cpp).
9. Clamp _DepthFlipScreen.x in UberShaderRenderQueue.SetRenderQueueExplicit
   (Assembly-CSharp__27.cpp) for Metal Reversed-Z.
10. Add iOS MFi / GCExtendedGamepad (e.g. GameSir) button and D-pad support to
    XboxControllerInput.GetAxis and XboxControllerInput.GetButton (Assembly-CSharp__29.cpp).
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

    # 1. Stub all AVProWindowsMediaPlugin P/Invoke methods so they never attempt to load AVProWindowsMedia.dll
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

    # 2. Clamp _DepthFlipScreen.x in AtlasSpriteTextureBinder_BindTo so z_ndc = (_DepthFlipScreen.x + 200)/1200
    # is always strictly inside (0.0, 1.0) on Metal Reversed-Z (ZTest Less -> MTLCompareFunctionGreater vs 0.0).
    old_depth_flip = """\t\tV_4 = G_B13_0;
\t\tfloat L_104 = V_4;
\t\t(&V_3)->___y = L_104;"""
    new_depth_flip = """\t\tV_4 = G_B13_0;
\t\tfloat L_104 = V_4;
\t\t(&V_3)->___y = L_104;
\t\tif ((&V_3)->___x < -100.0f || (&V_3)->___x > 900.0f) { (&V_3)->___x = 0.0f; }"""
    if "(&V_3)->___x < -100.0f" not in content:
        if old_depth_flip not in content:
            raise RuntimeError("Could not find AtlasSpriteTextureBinder_BindTo _DepthFlipScreen block in Assembly-CSharp__1.cpp")
        content = content.replace(old_depth_flip, new_depth_flip, 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Patched Assembly-CSharp__1.cpp ({count} AVProWindowsMediaPlugin stubs + AtlasSpriteTextureBinder _DepthFlipScreen clamp)")


def patch_assembly_csharp_11(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__11.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Guard MenuScreenManager.Instantiate against null prefabs (e.g. OptionsPrefab / PauseScreenPrefab on title screen)
    inst_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR GameObject_t76FEDD663AB33C991A9C9A23129337651094216F* MenuScreenManager_Instantiate_m792DCC5C8411B311F2866C149A325B618AD01E12"
    inst_body = """\tstatic bool s_Il2CppMethodInitialized;
\tif (!s_Il2CppMethodInitialized)
\t{
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&GameObject_AddComponent_TisLoadFromMasterAtStart_t9C25327BF5969C2858A43DF91C5D1F7F94D50586_m52E3EC4D7875B897D68BD318CD72941F41792CDF_RuntimeMethod_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Object_Instantiate_TisGameObject_t76FEDD663AB33C991A9C9A23129337651094216F_m831D2F71DF2AA6C93AFDFEFA04CF2CFC5FBBCDB4_RuntimeMethod_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&SaveSceneManager_t1245C60B6A57C75430C3A63679738D1F72A7AF1C_il2cpp_TypeInfo_var);
\t\ts_Il2CppMethodInitialized = true;
\t}
\tGameObject_t76FEDD663AB33C991A9C9A23129337651094216F* V_0 = NULL;
\t{
\t\tGameObject_t76FEDD663AB33C991A9C9A23129337651094216F* L_0 = ___0_prefab;
\t\til2cpp_codegen_runtime_class_init_inline(Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);
\t\tif (Object_op_Equality_mB6120F782D83091EF56A198FCEBCF066DB4A9605(L_0, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL))
\t\t{
\t\t\treturn (GameObject_t76FEDD663AB33C991A9C9A23129337651094216F*)NULL;
\t\t}
\t\tVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 L_1;
\t\tL_1 = Vector3_get_zero_m0C1249C3F25B1C70EAD3CC8B31259975A457AE39_inline(NULL);
\t\tQuaternion_tDA59F214EF07D7700B26E40E562F267AF7306974 L_2;
\t\tL_2 = Quaternion_get_identity_m7E701AE095ED10FD5EA0B50ABCFDE2EEFF2173A5_inline(NULL);
\t\tGameObject_t76FEDD663AB33C991A9C9A23129337651094216F* L_3;
\t\tL_3 = Object_Instantiate_TisGameObject_t76FEDD663AB33C991A9C9A23129337651094216F_m831D2F71DF2AA6C93AFDFEFA04CF2CFC5FBBCDB4(L_0, L_1, L_2, Object_Instantiate_TisGameObject_t76FEDD663AB33C991A9C9A23129337651094216F_m831D2F71DF2AA6C93AFDFEFA04CF2CFC5FBBCDB4_RuntimeMethod_var);
\t\tV_0 = L_3;
\t\tGameObject_t76FEDD663AB33C991A9C9A23129337651094216F* L_4 = V_0;
\t\tGameObject_t76FEDD663AB33C991A9C9A23129337651094216F* L_5 = ___0_prefab;
\t\tNullCheck(L_5);
\t\tString_t* L_6;
\t\tL_6 = Object_get_name_mAC2F6B897CF1303BA4249B4CB55271AFACBB6392(L_5, NULL);
\t\tNullCheck(L_4);
\t\tObject_set_name_mC79E6DC8FFD72479C90F0C4CC7F42A0FEAF5AE47(L_4, L_6, NULL);
\t\til2cpp_codegen_runtime_class_init_inline(SaveSceneManager_t1245C60B6A57C75430C3A63679738D1F72A7AF1C_il2cpp_TypeInfo_var);
\t\tSaveSceneManager_t1245C60B6A57C75430C3A63679738D1F72A7AF1C* L_7 = ((SaveSceneManager_t1245C60B6A57C75430C3A63679738D1F72A7AF1C_StaticFields*)il2cpp_codegen_static_fields_for(SaveSceneManager_t1245C60B6A57C75430C3A63679738D1F72A7AF1C_il2cpp_TypeInfo_var))->___Master;
\t\tGameObject_t76FEDD663AB33C991A9C9A23129337651094216F* L_8 = V_0;
\t\tif (L_7 != NULL)
\t\t{
\t\t\tSaveSceneManager_RegisterGameObject_m67EA4ADEF8A4A8EACD96FA755B21DF617D1EB14B(L_7, L_8, NULL);
\t\t}
\t\tGameObject_t76FEDD663AB33C991A9C9A23129337651094216F* L_9 = V_0;
\t\tNullCheck(L_9);
\t\tTransform_tB27202C6F4E36D225EE28A13E4D662BF99785DB1* L_10;
\t\tL_10 = GameObject_get_transform_m0BC10ADFA1632166AE5544BDF9038A2650C2AE56(L_9, NULL);
\t\tTransform_tB27202C6F4E36D225EE28A13E4D662BF99785DB1* L_11;
\t\tL_11 = Component_get_transform_m2919A1D81931E6932C7F06D4C2F0AB8DDA9A5371(__this, NULL);
\t\tNullCheck(L_10);
\t\tTransform_set_parent_m9BD5E563B539DD5BEC342736B03F97B38A243234(L_10, L_11, NULL);
\t\tGameObject_t76FEDD663AB33C991A9C9A23129337651094216F* L_12 = V_0;
\t\tNullCheck(L_12);
\t\tGameObject_SetActive_m638E92E1E75E519E5B24CF150B08CA8E0CDFAB92(L_12, (bool)0, NULL);
\t\tGameObject_t76FEDD663AB33C991A9C9A23129337651094216F* L_13 = V_0;
\t\tNullCheck(L_13);
\t\tLoadFromMasterAtStart_t9C25327BF5969C2858A43DF91C5D1F7F94D50586* L_14;
\t\tL_14 = GameObject_AddComponent_TisLoadFromMasterAtStart_t9C25327BF5969C2858A43DF91C5D1F7F94D50586_m52E3EC4D7875B897D68BD318CD72941F41792CDF(L_13, GameObject_AddComponent_TisLoadFromMasterAtStart_t9C25327BF5969C2858A43DF91C5D1F7F94D50586_m52E3EC4D7875B897D68BD318CD72941F41792CDF_RuntimeMethod_var);
\t\tGameObject_t76FEDD663AB33C991A9C9A23129337651094216F* L_15 = V_0;
\t\treturn L_15;
\t}"""
    content = replace_func_body(content, inst_decl, inst_body)

    # Also guard Utility_DontAssociateWithAnyScene(L_3, NULL) in Setup* methods when L_3 is NULL
    content = content.replace(
        "\t\tL_3 = MenuScreenManager_Instantiate_m792DCC5C8411B311F2866C149A325B618AD01E12(__this, L_2, NULL);\n"
        "\t\tUtility_DontAssociateWithAnyScene_m7F5E614627B34BF7A9A23BC4D04A92FB23D3A98B(L_3, NULL);",
        "\t\tL_3 = MenuScreenManager_Instantiate_m792DCC5C8411B311F2866C149A325B618AD01E12(__this, L_2, NULL);\n"
        "\t\tif (L_3 != NULL) { Utility_DontAssociateWithAnyScene_m7F5E614627B34BF7A9A23BC4D04A92FB23D3A98B(L_3, NULL); }",
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__11.cpp (MenuScreenManager.Instantiate null prefab guards)")


def patch_assembly_csharp_13(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__13.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Add external declarations needed in Assembly-CSharp__13.cpp
    extern_decls = (
        "IL2CPP_EXTERN_C String_t* _stringLiteral57731D1C7614FDA9B9F849E36B9C6D9B7278712C;\n"
        "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Renderer_set_enabled_m015E6D7B825528A31182F267234CC6A925F71DA8 (Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF* __this, bool ___0_value, const RuntimeMethod* method);\n"
        "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 Material_GetVector_mA2011D4DA2CC58003AE90DBF0802CF5EE31B014D (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, String_t* ___0_name, const RuntimeMethod* method);\n"
        "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Material_SetVector_m69444B8040D955821F241113446CC8713C9E12D1 (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, String_t* ___0_name, Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 ___1_value, const RuntimeMethod* method);\n"
        "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void OriPortShaderFallback__ctor_mA92EB12DE6E9C75F94389576A21DBED456F345C1 (OriPortShaderFallback_t8B81F7F3777F45910163AD5256AEF3336629DB06* __this, const RuntimeMethod* method);\n"
        "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void OriPortShaderFallback_PatchLoadedRenderers_m6207097F5CCA64E7C293C7E24CD958FAEC3B8444 (OriPortShaderFallback_t8B81F7F3777F45910163AD5256AEF3336629DB06* __this, const RuntimeMethod* method);\n"
        "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void OriPortManualPresenter_UpdateAlphaGrab_m6D5C8A797031A3CAABF1F73E449DA1A147570CEF (OriPortManualPresenter_t2F5F855B4DF012477351066DD463FB5872874118* __this, int32_t ___0_width, int32_t ___1_height, const RuntimeMethod* method);\n"
        "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void OriPortManualPresenter_RenderUserInterface_m546BED64DE0F3F78E0361CC7953676CF474D2161 (OriPortManualPresenter_t2F5F855B4DF012477351066DD463FB5872874118* __this, Camera_tA92CC927D7439999BC82DBEDC0AA45B470F9E184* ___0_mainCamera, const RuntimeMethod* method);\n"
    )
    render_frame_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void OriPortManualPresenter_RenderFrame_m9CADB5C9F1B1990254DE31AA31AAB8DA5F9F8052"
    if "OriPortManualPresenter_UpdateAlphaGrab_m6D5C8A797031A3CAABF1F73E449DA1A147570CEF (" not in content.split(render_frame_decl)[0]:
        content = content.replace(render_frame_decl, extern_decls + render_frame_decl, 1)

    # 1. In OriPortManualPresenter_RenderFrame:
    #    - Periodically run OriPortShaderFallback_PatchLoadedRenderers (every 15 frames) before Camera.Render()
    #    - Call OriPortManualPresenter_UpdateAlphaGrab(__this, V_2, V_3, NULL) after Camera.Render()
    #    - Call OriPortManualPresenter_RenderUserInterface(__this, V_1, NULL) after UpdateAlphaGrab()
    old_render_call = """\t\t\t\tShader_SetGlobalFloat_m8AA7A4D7D73914A00D9207D78621EDDF70602FB0(_stringLiteral682BF2EFA52E75C110EBBFF64FA09D54B09DA240, (-1.0f), NULL);
\t\t\t\tOriPortManualPresenter_set_IsRenderingPresentedFrame_m1760BA79F65488022AE1A93714CC89A44E71424E_inline((bool)1, NULL);
\t\t\t\tCamera_tA92CC927D7439999BC82DBEDC0AA45B470F9E184* L_71 = V_1;
\t\t\t\tNullCheck(L_71);
\t\t\t\tCamera_Render_m6089001EB6710DA9A21C87185D65922F13A24509(L_71, NULL);
\t\t\t\tgoto IL_01b7;"""

    new_render_call = """\t\t\t\tstatic OriPortShaderFallback_t8B81F7F3777F45910163AD5256AEF3336629DB06* s_fallbackObj = NULL;
\t\t\t\tstatic int32_t s_patchCounter = 0;
\t\t\t\tif (s_fallbackObj == NULL)
\t\t\t\t{
\t\t\t\t\tstatic OriPortShaderFallback_t8B81F7F3777F45910163AD5256AEF3336629DB06 s_fallbackStorage;
\t\t\t\t\tmemset(&s_fallbackStorage, 0, sizeof(s_fallbackStorage));
\t\t\t\t\ts_fallbackObj = &s_fallbackStorage;
\t\t\t\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteralD14C58C1EE361C9330F36F7B5E51A6947D158C6E);
\t\t\t\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral7078454B1E5C2E624B80831BA98D6DD13E9272FD);
\t\t\t\t\tOriPortShaderFallback__ctor_mA92EB12DE6E9C75F94389576A21DBED456F345C1(s_fallbackObj, NULL);
\t\t\t\t\ts_fallbackObj->___m_fallbackShader = Shader_Find_m183AA54F78320212DDEC811592F98456898A41C5(_stringLiteralD14C58C1EE361C9330F36F7B5E51A6947D158C6E, NULL);
\t\t\t\t\ts_fallbackObj->___m_distanceFieldTextShader = Shader_Find_m183AA54F78320212DDEC811592F98456898A41C5(_stringLiteral7078454B1E5C2E624B80831BA98D6DD13E9272FD, NULL);
\t\t\t\t}
\t\t\t\tif ((s_patchCounter++ % 15) == 0 && s_fallbackObj != NULL)
\t\t\t\t{
\t\t\t\t\tOriPortShaderFallback_PatchLoadedRenderers_m6207097F5CCA64E7C293C7E24CD958FAEC3B8444(s_fallbackObj, NULL);
\t\t\t\t}
\t\t\t\tShader_SetGlobalFloat_m8AA7A4D7D73914A00D9207D78621EDDF70602FB0(_stringLiteral682BF2EFA52E75C110EBBFF64FA09D54B09DA240, (-1.0f), NULL);
\t\t\t\tOriPortManualPresenter_set_IsRenderingPresentedFrame_m1760BA79F65488022AE1A93714CC89A44E71424E_inline((bool)1, NULL);
\t\t\t\tCamera_tA92CC927D7439999BC82DBEDC0AA45B470F9E184* L_71 = V_1;
\t\t\t\tNullCheck(L_71);
\t\t\t\tCamera_Render_m6089001EB6710DA9A21C87185D65922F13A24509(L_71, NULL);
\t\t\t\tOriPortManualPresenter_UpdateAlphaGrab_m6D5C8A797031A3CAABF1F73E449DA1A147570CEF(__this, V_2, V_3, NULL);
\t\t\t\tOriPortManualPresenter_RenderUserInterface_m546BED64DE0F3F78E0361CC7953676CF474D2161(__this, V_1, NULL);
\t\t\t\tgoto IL_01b7;"""

    if "OriPortManualPresenter_RenderUserInterface_m546BED64DE0F3F78E0361CC7953676CF474D2161(__this, V_1, NULL);" not in content:
        if old_render_call not in content:
            raise RuntimeError("Could not find Camera_Render block in OriPortManualPresenter_RenderFrame")
        content = content.replace(old_render_call, new_render_call, 1)

    # 2. In OriPortShaderFallback_PatchLoadedRenderers:
    #    - Initialize _stringLiteral57731D1C7614FDA9B9F849E36B9C6D9B7278712C ("_DepthFlipScreen")
    #    - Clamp _DepthFlipScreen.x on every material that has it so Metal Reversed-Z ZTest Less passes
    #    - Disable any renderer using Hidden/EarlyZWrite (Renderer_set_enabled(V_8, false)) so dummy opaque prepass meshes don't draw or occlude
    old_meta = "il2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteralC4909D7574FBD1AE3EE1C0E4055C75960236DBFD);"
    new_meta = (
        old_meta
        + "\n\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral57731D1C7614FDA9B9F849E36B9C6D9B7278712C);"
    )
    if "_stringLiteral57731D1C7614FDA9B9F849E36B9C6D9B7278712C);" not in content:
        content = content.replace(old_meta, new_meta, 1)

    old_earlyz_block = """IL_01bc:
\t{
\t\tString_t* L_76 = V_13;
\t\tbool L_77;
\t\tL_77 = String_op_Equality_m030E1B219352228970A076136E455C4E568C02C1(L_76, _stringLiteral1E5A05C3CB0E65E4EC72B4E86353C4177C469AEA, NULL);
\t\tif (!L_77)
\t\t{
\t\t\tgoto IL_0247;
\t\t}
\t}"""

    new_earlyz_block = """IL_01bc:
\t{
\t\tif (V_12 != NULL && Material_HasProperty_mC09A83B44E368A217F606DD4954FA080CC03EC6C(V_12, _stringLiteral57731D1C7614FDA9B9F849E36B9C6D9B7278712C, NULL))
\t\t{
\t\t\tVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 df = Material_GetVector_mA2011D4DA2CC58003AE90DBF0802CF5EE31B014D(V_12, _stringLiteral57731D1C7614FDA9B9F849E36B9C6D9B7278712C, NULL);
\t\t\tif (df.___x < -100.0f || df.___x > 900.0f)
\t\t\t{
\t\t\t\tdf.___x = 0.0f;
\t\t\t\tMaterial_SetVector_m69444B8040D955821F241113446CC8713C9E12D1(V_12, _stringLiteral57731D1C7614FDA9B9F849E36B9C6D9B7278712C, df, NULL);
\t\t\t}
\t\t}
\t\tString_t* L_76 = V_13;
\t\tbool L_77;
\t\tL_77 = String_op_Equality_m030E1B219352228970A076136E455C4E568C02C1(L_76, _stringLiteral1E5A05C3CB0E65E4EC72B4E86353C4177C469AEA, NULL);
\t\tif (!L_77)
\t\t{
\t\t\tgoto IL_0247;
\t\t}
\t\tif (V_8 != NULL)
\t\t{
\t\t\tRenderer_set_enabled_m015E6D7B825528A31182F267234CC6A925F71DA8(V_8, (bool)0, NULL);
\t\t}
\t}"""

    if "Renderer_set_enabled_m015E6D7B825528A31182F267234CC6A925F71DA8(V_8, (bool)0, NULL);" not in content:
        if old_earlyz_block not in content:
            raise RuntimeError("Could not find IL_01bc block in OriPortShaderFallback_PatchLoadedRenderers")
        content = content.replace(old_earlyz_block, new_earlyz_block, 1)

    # 3. Enable OriPortTouchControls on the title screen as well as in gameplay
    touch_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool OriPortTouchControls_get_GameplayControlsEnabled_mF19030CD53AA9F354B8004DF880315F11D19BFA5"
    touch_body = """\tstatic bool s_Il2CppMethodInitialized;
\tif (!s_Il2CppMethodInitialized)
\t{
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&OriPortTouchControls_tA5DF2EC3B4DF297414247C1AD8789A9A15ABC611_il2cpp_TypeInfo_var);
\t\ts_Il2CppMethodInitialized = true;
\t}
\t{
\t\til2cpp_codegen_runtime_class_init_inline(OriPortTouchControls_tA5DF2EC3B4DF297414247C1AD8789A9A15ABC611_il2cpp_TypeInfo_var);
\t\treturn OriPortTouchControls_get_SupportedPlatform_mA634742AAD4C96C71BBFC1E471F194EA0450CF51(NULL);
\t}"""
    content = replace_func_body(content, touch_decl, touch_body)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__13.cpp (OriPortManualPresenter UI/AlphaGrab/Fallback + EarlyZWrite disable + TouchControls on title screen)")


def patch_assembly_csharp_27(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__27.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Clamp L_15 (z) in UberShaderRenderQueue_SetRenderQueueExplicit so _DepthFlipScreen.x stays in [-100, 900]
    old_vec_set = "\t\tfloat L_15 = ___1_z;\n\t\tVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_16 = V_1;"
    new_vec_set = (
        "\t\tfloat L_15 = ___1_z;\n"
        "\t\tif (L_15 < -100.0f) { L_15 = -100.0f; } else if (L_15 > 900.0f) { L_15 = 900.0f; }\n"
        "\t\tVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 L_16 = V_1;"
    )
    if "if (L_15 < -100.0f)" not in content:
        if old_vec_set not in content:
            raise RuntimeError("Could not find L_15 assignment in UberShaderRenderQueue_SetRenderQueueExplicit")
        content = content.replace(old_vec_set, new_vec_set, 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__27.cpp (UberShaderRenderQueue _DepthFlipScreen.x clamp)")


def patch_assembly_csharp_29(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__29.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add iOS MFi / GCExtendedGamepad D-Pad KeyCode fallback to XboxControllerInput_GetAxis (Axis 4 = DPadX, Axis 5 = DPadY)
    #    KeyCode.JoystickButton4 = 334 (DPad Up), 5 = 335 (DPad Right), 6 = 336 (DPad Down), 7 = 337 (DPad Left)
    old_dpadx = """IL_0100:
\t{
\t\til2cpp_codegen_runtime_class_init_inline(XboxControllerInput_t02A09005482D04ABAD089F7F782AD34482369DC0_il2cpp_TypeInfo_var);
\t\tStringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_50 = ((XboxControllerInput_t02A09005482D04ABAD089F7F782AD34482369DC0_StaticFields*)il2cpp_codegen_static_fields_for(XboxControllerInput_t02A09005482D04ABAD089F7F782AD34482369DC0_il2cpp_TypeInfo_var))->___m_joystickAxis6Map;
\t\tint32_t L_51 = V_0;
\t\tNullCheck(L_50);
\t\tint32_t L_52 = L_51;
\t\tString_t* L_53 = (L_50)->GetAt(static_cast<il2cpp_array_size_t>(L_52));
\t\tfloat L_54;
\t\tL_54 = MoonInput_GetAxis_m5BA9804A3E137BB0D0A3ED0A5C9C4917C63F677C(L_53, NULL);
\t\treturn L_54;
\t}

IL_010d:
\t{
\t\til2cpp_codegen_runtime_class_init_inline(XboxControllerInput_t02A09005482D04ABAD089F7F782AD34482369DC0_il2cpp_TypeInfo_var);
\t\tStringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_55 = ((XboxControllerInput_t02A09005482D04ABAD089F7F782AD34482369DC0_StaticFields*)il2cpp_codegen_static_fields_for(XboxControllerInput_t02A09005482D04ABAD089F7F782AD34482369DC0_il2cpp_TypeInfo_var))->___m_joystickAxis7Map;
\t\tint32_t L_56 = V_0;
\t\tNullCheck(L_55);
\t\tint32_t L_57 = L_56;
\t\tString_t* L_58 = (L_55)->GetAt(static_cast<il2cpp_array_size_t>(L_57));
\t\tfloat L_59;
\t\tL_59 = MoonInput_GetAxis_m5BA9804A3E137BB0D0A3ED0A5C9C4917C63F677C(L_58, NULL);
\t\treturn L_59;
\t}"""

    new_dpadx = """IL_0100:
\t{
\t\tif (MoonInput_GetKey_m3AA2E312BBBFF5E96BD036637D7312AB7A8540FD(335, NULL)) { return 1.0f; }
\t\tif (MoonInput_GetKey_m3AA2E312BBBFF5E96BD036637D7312AB7A8540FD(337, NULL)) { return -1.0f; }
\t\til2cpp_codegen_runtime_class_init_inline(XboxControllerInput_t02A09005482D04ABAD089F7F782AD34482369DC0_il2cpp_TypeInfo_var);
\t\tStringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_50 = ((XboxControllerInput_t02A09005482D04ABAD089F7F782AD34482369DC0_StaticFields*)il2cpp_codegen_static_fields_for(XboxControllerInput_t02A09005482D04ABAD089F7F782AD34482369DC0_il2cpp_TypeInfo_var))->___m_joystickAxis6Map;
\t\tint32_t L_51 = V_0;
\t\tNullCheck(L_50);
\t\tint32_t L_52 = L_51;
\t\tString_t* L_53 = (L_50)->GetAt(static_cast<il2cpp_array_size_t>(L_52));
\t\tfloat L_54;
\t\tL_54 = MoonInput_GetAxis_m5BA9804A3E137BB0D0A3ED0A5C9C4917C63F677C(L_53, NULL);
\t\treturn L_54;
\t}

IL_010d:
\t{
\t\tif (MoonInput_GetKey_m3AA2E312BBBFF5E96BD036637D7312AB7A8540FD(334, NULL)) { return 1.0f; }
\t\tif (MoonInput_GetKey_m3AA2E312BBBFF5E96BD036637D7312AB7A8540FD(336, NULL)) { return -1.0f; }
\t\til2cpp_codegen_runtime_class_init_inline(XboxControllerInput_t02A09005482D04ABAD089F7F782AD34482369DC0_il2cpp_TypeInfo_var);
\t\tStringU5BU5D_t7674CD946EC0CE7B3AE0BE70E6EE85F2ECD9F248* L_55 = ((XboxControllerInput_t02A09005482D04ABAD089F7F782AD34482369DC0_StaticFields*)il2cpp_codegen_static_fields_for(XboxControllerInput_t02A09005482D04ABAD089F7F782AD34482369DC0_il2cpp_TypeInfo_var))->___m_joystickAxis7Map;
\t\tint32_t L_56 = V_0;
\t\tNullCheck(L_55);
\t\tint32_t L_57 = L_56;
\t\tString_t* L_58 = (L_55)->GetAt(static_cast<il2cpp_array_size_t>(L_57));
\t\tfloat L_59;
\t\tL_59 = MoonInput_GetAxis_m5BA9804A3E137BB0D0A3ED0A5C9C4917C63F677C(L_58, NULL);
\t\treturn L_59;
\t}"""

    if "MoonInput_GetKey_m3AA2E312BBBFF5E96BD036637D7312AB7A8540FD(335, NULL)" not in content:
        if old_dpadx not in content:
            raise RuntimeError("Could not find IL_0100 / IL_010d DPad blocks in XboxControllerInput_GetAxis")
        content = content.replace(old_dpadx, new_dpadx, 1)

    # 2. Add iOS MFi / GCExtendedGamepad KeyCode support in XboxControllerInput_GetButton
    #    before the Windows InputManager switch:
    #    - ButtonA (0): KeyCode.JoystickButton14 (344, MFi A) || KeyCode.JoystickButton0 (330)
    #    - ButtonX (1): KeyCode.JoystickButton15 (345, MFi X) || KeyCode.JoystickButton2 (332)
    #    - ButtonY (2): KeyCode.JoystickButton12 (342, MFi Y) || KeyCode.JoystickButton3 (333)
    #    - ButtonB (3): KeyCode.JoystickButton13 (343, MFi B) || KeyCode.JoystickButton1 (331)
    #    - LeftTrigger (4): KeyCode.JoystickButton10 (340, MFi L2)
    #    - RightTrigger (5): KeyCode.JoystickButton11 (341, MFi R2)
    #    - LeftShoulder (6): KeyCode.JoystickButton8 (338, MFi L1)
    #    - RightShoulder (7): KeyCode.JoystickButton9 (339, MFi R1)
    #    - LeftStick (8): KeyCode.JoystickButton18 (348, MFi L3)
    #    - RightStick (9): KeyCode.JoystickButton19 (349, MFi R3)
    #    - Select (10): KeyCode.JoystickButton16 (346)
    #    - Start (11): KeyCode.JoystickButton0 (330, MFi Menu) || KeyCode.JoystickButton7 (337)
    old_btn_switch = """\t{
\t\tint32_t L_38 = ___0_button;
\t\til2cpp_codegen_runtime_class_init_inline(PlayerInputRebinding_t780DD2FDE54D024B9B99531C52EC1D4EA3C6A150_il2cpp_TypeInfo_var);"""

    new_btn_switch = """\t{
\t\tswitch (___0_button)
\t\t{
\t\t\tcase 0: if (MoonInput_GetKey_m3AA2E312BBBFF5E96BD036637D7312AB7A8540FD(344, NULL)) return true; break;
\t\t\tcase 1: if (MoonInput_GetKey_m3AA2E312BBBFF5E96BD036637D7312AB7A8540FD(345, NULL)) return true; break;
\t\t\tcase 2: if (MoonInput_GetKey_m3AA2E312BBBFF5E96BD036637D7312AB7A8540FD(342, NULL)) return true; break;
\t\t\tcase 3: if (MoonInput_GetKey_m3AA2E312BBBFF5E96BD036637D7312AB7A8540FD(343, NULL)) return true; break;
\t\t\tcase 4: if (MoonInput_GetKey_m3AA2E312BBBFF5E96BD036637D7312AB7A8540FD(340, NULL)) return true; break;
\t\t\tcase 5: if (MoonInput_GetKey_m3AA2E312BBBFF5E96BD036637D7312AB7A8540FD(341, NULL)) return true; break;
\t\t\tcase 6: if (MoonInput_GetKey_m3AA2E312BBBFF5E96BD036637D7312AB7A8540FD(338, NULL)) return true; break;
\t\t\tcase 7: if (MoonInput_GetKey_m3AA2E312BBBFF5E96BD036637D7312AB7A8540FD(339, NULL)) return true; break;
\t\t\tcase 8: if (MoonInput_GetKey_m3AA2E312BBBFF5E96BD036637D7312AB7A8540FD(348, NULL)) return true; break;
\t\t\tcase 9: if (MoonInput_GetKey_m3AA2E312BBBFF5E96BD036637D7312AB7A8540FD(349, NULL)) return true; break;
\t\t\tcase 10: if (MoonInput_GetKey_m3AA2E312BBBFF5E96BD036637D7312AB7A8540FD(346, NULL)) return true; break;
\t\t\tcase 11: if (MoonInput_GetKey_m3AA2E312BBBFF5E96BD036637D7312AB7A8540FD(330, NULL)) return true; break;
\t\t}
\t\tint32_t L_38 = ___0_button;
\t\til2cpp_codegen_runtime_class_init_inline(PlayerInputRebinding_t780DD2FDE54D024B9B99531C52EC1D4EA3C6A150_il2cpp_TypeInfo_var);"""

    if "MoonInput_GetKey_m3AA2E312BBBFF5E96BD036637D7312AB7A8540FD(344, NULL)" not in content:
        if old_btn_switch not in content:
            raise RuntimeError("Could not find PlayerInputRebinding block in XboxControllerInput_GetButton")
        content = content.replace(old_btn_switch, new_btn_switch, 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__29.cpp (iOS MFi / GameSir controller support)")


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
    patch_assembly_csharp_11(cpp_dir)
    patch_assembly_csharp_13(cpp_dir)
    patch_assembly_csharp_27(cpp_dir)
    patch_assembly_csharp_29(cpp_dir)
    print("All iOS IL2CPP runtime patches applied successfully!")


if __name__ == "__main__":
    main()
