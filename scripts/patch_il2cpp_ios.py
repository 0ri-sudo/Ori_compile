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

    # 2. Prevent WorldMapUI from crashing in Awake when GameMapUI.Instance is still null (because gameMap.prefab
    #    is instantiated inactive by MenuScreenManager), and immediately deactivate worldMapScene after its
    #    Awake initialization if GameMapUI is not currently visible so worldMapScene's perspCamera never
    #    hijacks the in-game camera during gameplay!
    old_wm_awake = """\t\tGameMapUI_t0C9081A1B2D066C0431FEE3F737BF5FD6C7023EF* L_3 = ((GameMapUI_t0C9081A1B2D066C0431FEE3F737BF5FD6C7023EF_StaticFields*)il2cpp_codegen_static_fields_for(GameMapUI_t0C9081A1B2D066C0431FEE3F737BF5FD6C7023EF_il2cpp_TypeInfo_var))->___Instance;
\t\tNullCheck(L_3);
\t\tTransform_tB27202C6F4E36D225EE28A13E4D662BF99785DB1* L_4 = L_3->___Group;
\t\tNullCheck(L_2);
\t\tTransform_set_parent_m9BD5E563B539DD5BEC342736B03F97B38A243234(L_2, L_4, NULL);"""
    new_wm_awake = """\t\tGameMapUI_t0C9081A1B2D066C0431FEE3F737BF5FD6C7023EF* L_3 = ((GameMapUI_t0C9081A1B2D066C0431FEE3F737BF5FD6C7023EF_StaticFields*)il2cpp_codegen_static_fields_for(GameMapUI_t0C9081A1B2D066C0431FEE3F737BF5FD6C7023EF_il2cpp_TypeInfo_var))->___Instance;
\t\tif (L_3 != NULL && L_2 != NULL)
\t\t{
\t\t\tTransform_tB27202C6F4E36D225EE28A13E4D662BF99785DB1* L_4 = L_3->___Group;
\t\t\tTransform_set_parent_m9BD5E563B539DD5BEC342736B03F97B38A243234(L_2, L_4, NULL);
\t\t}"""
    if "if (L_3 != NULL && L_2 != NULL)" not in content:
        if old_wm_awake not in content:
            raise RuntimeError("Could not find WorldMapUI_Awake GameMapUI.Instance.Group block in Assembly-CSharp__28.cpp")
        content = content.replace(old_wm_awake, new_wm_awake, 1)

    old_wm_activate = """\t\tGameMapUI_t0C9081A1B2D066C0431FEE3F737BF5FD6C7023EF* L_1 = ((GameMapUI_t0C9081A1B2D066C0431FEE3F737BF5FD6C7023EF_StaticFields*)il2cpp_codegen_static_fields_for(GameMapUI_t0C9081A1B2D066C0431FEE3F737BF5FD6C7023EF_il2cpp_TypeInfo_var))->___Instance;
\t\tNullCheck(L_1);
\t\tbool L_2;"""
    new_wm_activate = """\t\tGameMapUI_t0C9081A1B2D066C0431FEE3F737BF5FD6C7023EF* L_1 = ((GameMapUI_t0C9081A1B2D066C0431FEE3F737BF5FD6C7023EF_StaticFields*)il2cpp_codegen_static_fields_for(GameMapUI_t0C9081A1B2D066C0431FEE3F737BF5FD6C7023EF_il2cpp_TypeInfo_var))->___Instance;
\t\tNullCheck(L_1);
\t\tif (L_1->___Group != NULL)
\t\t{
\t\t\tTransform_tB27202C6F4E36D225EE28A13E4D662BF99785DB1* wmTrans = Component_get_transform_m2919A1D81931E6932C7F06D4C2F0AB8DDA9A5371(__this, NULL);
\t\t\tif (wmTrans != NULL) { Transform_set_parent_m9BD5E563B539DD5BEC342736B03F97B38A243234(wmTrans, L_1->___Group, NULL); }
\t\t}
\t\tbool L_2;"""
    if "if (L_1->___Group != NULL)" not in content:
        if old_wm_activate not in content:
            raise RuntimeError("Could not find WorldMapUI_Activate block in Assembly-CSharp__28.cpp")
        content = content.replace(old_wm_activate, new_wm_activate, 1)

    old_wm_loaded = """\t\tGameObject_t76FEDD663AB33C991A9C9A23129337651094216F* L_10;
\t\tL_10 = Component_get_gameObject_m57AEFBB14DB39EC476F740BA000E170355DE691B(L_9, NULL);
\t\tNullCheck(L_10);
\t\tGameObject_SetActive_m638E92E1E75E519E5B24CF150B08CA8E0CDFAB92(L_10, (bool)1, NULL);"""
    new_wm_loaded = """\t\tGameObject_t76FEDD663AB33C991A9C9A23129337651094216F* L_10;
\t\tL_10 = Component_get_gameObject_m57AEFBB14DB39EC476F740BA000E170355DE691B(L_9, NULL);
\t\tNullCheck(L_10);
\t\tGameObject_SetActive_m638E92E1E75E519E5B24CF150B08CA8E0CDFAB92(L_10, (bool)1, NULL);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&GameMapUI_t0C9081A1B2D066C0431FEE3F737BF5FD6C7023EF_il2cpp_TypeInfo_var);
\t\tGameMapUI_t0C9081A1B2D066C0431FEE3F737BF5FD6C7023EF* gmInst = ((GameMapUI_t0C9081A1B2D066C0431FEE3F737BF5FD6C7023EF_StaticFields*)il2cpp_codegen_static_fields_for(GameMapUI_t0C9081A1B2D066C0431FEE3F737BF5FD6C7023EF_il2cpp_TypeInfo_var))->___Instance;
\t\tif (gmInst == NULL || !gmInst->___m_isVisible)
\t\t{
\t\t\tGameObject_SetActive_m638E92E1E75E519E5B24CF150B08CA8E0CDFAB92(L_10, (bool)0, NULL);
\t\t}"""
    if "gmInst == NULL || !gmInst->___m_isVisible" not in content:
        if old_wm_loaded not in content:
            raise RuntimeError("Could not find WorldMapUI_OnFinishedLoading SetActive block in Assembly-CSharp__28.cpp")
        content = content.replace(old_wm_loaded, new_wm_loaded, 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__28.cpp (WindowManager user32.dll stubs + WorldMapUI camera hijack fix)")


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


def patch_assembly_csharp_3(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__3.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. CameraPuppetController.Reset() is called by CameraGoThroughScrollLocks during
    #    GameplayToCinematicAnimator transitions! It must NOT null out ___CinematicPuppet
    #    (which was just assigned by GameplayToCinematicAnimator.Start()), otherwise
    #    cutscene camera animations in the Prologue never move the camera!
    reset_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void CameraPuppetController_Reset_m4707731712033B6CC8BE8954FF27AFACF81A5D8C"
    reset_body = """\t{
\t\tCameraPuppetController_SetTween_m0DADFF57AE798BFE43E09ABD5D3E30B408A21A39_inline(__this, (0.0f), NULL);
\t\tCameraPuppetController_ClearWideScreenAdjustments_mABDC758FA3A9F15D4B69D568FDB72FC24B951D10(__this, NULL);
\t\tCameraPuppetController_UpdatePuppet_m83FF6BE15B71CDAE5E3AA80C885D3F2BF59794ED(__this, NULL);
\t\treturn;
\t}"""
    content = replace_func_body(content, reset_decl, reset_body)

    # 2. Add helper OriPort_SnapCameraToCurrentCharacter() so SeinPlaceholder can snap the gameplay camera
    #    to Ori when spawning in normal gameplay (e.g. when skipping prologue), WITHOUT overriding an
    #    active cutscene camera puppet (when CinematicPuppet != NULL && Tween > 0.001f).
    snap_helper = """IL2CPP_EXTERN_C RuntimeClass* Cameras_t7935DA243CF368EB505A27E50005C968D54D5A90_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void CameraPuppetController_Reset_m4707731712033B6CC8BE8954FF27AFACF81A5D8C (CameraPuppetController_tE58C8D776D2A6D6F92B40603A306EB81D2509F10* __this, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void GameplayCamera_GoToChaseMode_mFFC2F96AFB013160811FCF9DBACC7EB92561EB40 (GameplayCamera_t0939DE616725B1ED6EEBFB571FAFFE64C578EF00* __this, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void GameplayCamera_MoveCameraToTargetInstantly_m74A1E7974672F8B1DEFE7756070B1A7B3072F2B6 (GameplayCamera_t0939DE616725B1ED6EEBFB571FAFFE64C578EF00* __this, bool ___0_updateTargetPosition, const RuntimeMethod* method);

IL2CPP_EXTERN_C void OriPort_SnapCameraToCurrentCharacter()
{
\tstatic bool s_init = false;
\tif (!s_init)
\t{
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Cameras_t7935DA243CF368EB505A27E50005C968D54D5A90_il2cpp_TypeInfo_var);
\t\ts_init = true;
\t}
\ttry
\t{
\t\tGameplayCamera_t0939DE616725B1ED6EEBFB571FAFFE64C578EF00* cam = ((Cameras_t7935DA243CF368EB505A27E50005C968D54D5A90_StaticFields*)il2cpp_codegen_static_fields_for(Cameras_t7935DA243CF368EB505A27E50005C968D54D5A90_il2cpp_TypeInfo_var))->___Current;
\t\tif (cam != NULL)
\t\t{
\t\t\tCameraController_tDC4FF0FA10418272A26E5E7539156F4F4A98E8C5* ctrl = cam->___Controller;
\t\t\tif (ctrl != NULL && ctrl->___PuppetController != NULL && ctrl->___PuppetController->___CinematicPuppet != NULL && ctrl->___PuppetController->___Tween > 0.001f)
\t\t\t{
\t\t\t\tGameplayCamera_ChangeTargetToCurrentCharacter_m9AC01DA2753D17D03CFFB4AA54950E843A49BEDF(cam, NULL);
\t\t\t\treturn;
\t\t\t}
\t\t\tif (ctrl != NULL && ctrl->___PuppetController != NULL)
\t\t\t{
\t\t\t\tctrl->___PuppetController->___CinematicPuppet = (Transform_tB27202C6F4E36D225EE28A13E4D662BF99785DB1*)NULL;
\t\t\t\tIl2CppCodeGenWriteBarrier((void**)(&ctrl->___PuppetController->___CinematicPuppet), (void*)(Transform_tB27202C6F4E36D225EE28A13E4D662BF99785DB1*)NULL);
\t\t\t\tCameraPuppetController_Reset_m4707731712033B6CC8BE8954FF27AFACF81A5D8C(ctrl->___PuppetController, NULL);
\t\t\t}
\t\t\tGameplayCamera_ChangeTargetToCurrentCharacter_m9AC01DA2753D17D03CFFB4AA54950E843A49BEDF(cam, NULL);
\t\t\tGameplayCamera_GoToChaseMode_mFFC2F96AFB013160811FCF9DBACC7EB92561EB40(cam, NULL);
\t\t\tGameplayCamera_MoveCameraToTargetInstantly_m74A1E7974672F8B1DEFE7756070B1A7B3072F2B6(cam, (bool)1, NULL);
\t\t}
\t}
\tcatch (Il2CppExceptionWrapper&)
\t{
\t}
}
"""
    old_snap_idx = content.find("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void CameraPuppetController_OnGameReset_mB50FE1A9F4211CBC1D1EBC9B942F7F56C4B29CC0")
    reset_def = reset_decl + " (CameraPuppetController_tE58C8D776D2A6D6F92B40603A306EB81D2509F10* __this, const RuntimeMethod* method) \n{"
    if reset_def not in content:
        reset_def = reset_decl + " (CameraPuppetController_tE58C8D776D2A6D6F92B40603A306EB81D2509F10* __this, const RuntimeMethod* method)\n{"
    reset_idx = content.find(reset_def)
    if old_snap_idx != -1 and reset_idx != -1:
        after_ongamereset = content.find("return;\n\t}\n}", old_snap_idx)
        if after_ongamereset != -1 and after_ongamereset < reset_idx:
            block_start = after_ongamereset + len("return;\n\t}\n}\n")
            content = content[:block_start] + snap_helper + content[reset_idx:]

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__3.cpp (CameraPuppetController.Reset preserve CinematicPuppet + OriPort_SnapCameraToCurrentCharacter cutscene guard)")


def patch_assembly_csharp_10(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__10.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. On iOS / mobile, shader prewarming is skipped, so IsWarmingShadersCondition.Validate()
    #    must return true so the introLogos endSequence does not wait forever at step
    #    "06. Wait until Is Warming Shaders Condition" before loading titleScreenSwallowsNest.
    validate_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool IsWarmingShadersCondition_Validate_mFCFCACC946962EA37D62CF20817494939A4F0ADC"
    validate_body = "\treturn (bool)1;"
    content = replace_func_body(content, validate_decl, validate_body)

    # 2. LateStartHook destroys its own GameObject on frame 1 (in Start()), so any scene loaded
    #    later via SceneManager/GoToSceneController that calls LateStartHook.AddLateStartMethod()
    #    would otherwise enqueue callbacks into LateStartHook.Actions that never run!
    #    Invoke the callback immediately if non-null.
    latestart_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void LateStartHook_AddLateStartMethod_m0BF28236D8E0D47595B8DFA72EFD6142CBD04652"
    latestart_body = """\tif (___0_method != NULL)
\t{
\t\tAction_Invoke_m7126A54DACA72B845424072887B5F3A51FC3808E_inline(___0_method, NULL);
\t}
\treturn;"""
    content = replace_func_body(content, latestart_decl, latestart_body)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__10.cpp (IsWarmingShadersCondition.Validate -> true + LateStartHook immediate invoke)")


def patch_assembly_csharp_11(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__11.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. When LoadingBootstrap skips shader prewarming on mobile, also mark UberShaderPrewarmer.IsComplete = true
    old_skip_check = "((UberShaderPrewarmer_t82F72BE4A89799766DCDFA838F76DA4FD5625E31_StaticFields*)il2cpp_codegen_static_fields_for(UberShaderPrewarmer_t82F72BE4A89799766DCDFA838F76DA4FD5625E31_il2cpp_TypeInfo_var))->___s_skipLoadedCheck = (bool)1;"
    new_skip_check = (
        "((UberShaderPrewarmer_t82F72BE4A89799766DCDFA838F76DA4FD5625E31_StaticFields*)il2cpp_codegen_static_fields_for(UberShaderPrewarmer_t82F72BE4A89799766DCDFA838F76DA4FD5625E31_il2cpp_TypeInfo_var))->___s_skipLoadedCheck = (bool)1;\n"
        "\t\t((UberShaderPrewarmer_t82F72BE4A89799766DCDFA838F76DA4FD5625E31_StaticFields*)il2cpp_codegen_static_fields_for(UberShaderPrewarmer_t82F72BE4A89799766DCDFA838F76DA4FD5625E31_il2cpp_TypeInfo_var))->___IsComplete = (bool)1;"
    )
    if "___IsComplete = (bool)1;" not in content:
        if old_skip_check not in content:
            raise RuntimeError("Could not find ___s_skipLoadedCheck assignment in LoadingBootstrap (Assembly-CSharp__11.cpp)")
        content = content.replace(old_skip_check, new_skip_check)

    # 2. Guard MenuScreenManager.Instantiate against null prefabs (e.g. OptionsPrefab / PauseScreenPrefab on title screen)
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

    # 3. On titleScreenSwallowsNest, MenuScreenManager.OptionsPrefab is null in the scene inspector,
    #    so clicking "Help & Options" on the title screen showed nothing because OptionsScreen.Instance was null!
    #    Load "optionsScreen" from Resources if ___0_optionsPrefab is null.
    setup_opt_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void MenuScreenManager_SetupOptionsScreen_m4319F519B9C1604B13FBBEFEA42618805497B653"
    setup_opt_extern = (
        "IL2CPP_EXTERN_C const RuntimeMethod* Resources_Load_TisGameObject_t76FEDD663AB33C991A9C9A23129337651094216F_m496A3B1B60A28F5E0397043974B848C9157B625A_RuntimeMethod_var;\n"
        "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR RuntimeObject* Resources_Load_TisRuntimeObject_mD1AF6299B14F87ED1D1A6199A51480919F7C79D7_gshared (String_t* ___0_path, const RuntimeMethod* method);\n"
    )
    if "Resources_Load_TisGameObject_t76FEDD663AB33C991A9C9A23129337651094216F_m496A3B1B60A28F5E0397043974B848C9157B625A_RuntimeMethod_var" not in content:
        content = content.replace(setup_opt_decl, setup_opt_extern + setup_opt_decl, 1)

    setup_opt_body = """\tstatic bool s_Il2CppMethodInitialized;
\tif (!s_Il2CppMethodInitialized)
\t{
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&OptionsScreen_t24FF687BD9C0A19DACB887A477884D897299E340_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Resources_Load_TisGameObject_t76FEDD663AB33C991A9C9A23129337651094216F_m496A3B1B60A28F5E0397043974B848C9157B625A_RuntimeMethod_var);
\t\ts_Il2CppMethodInitialized = true;
\t}
\t{
\t\tOptionsScreen_t24FF687BD9C0A19DACB887A477884D897299E340* L_0 = ((OptionsScreen_t24FF687BD9C0A19DACB887A477884D897299E340_StaticFields*)il2cpp_codegen_static_fields_for(OptionsScreen_t24FF687BD9C0A19DACB887A477884D897299E340_il2cpp_TypeInfo_var))->___Instance;
\t\til2cpp_codegen_runtime_class_init_inline(Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);
\t\tbool L_1;
\t\tL_1 = Object_op_Equality_mB6120F782D83091EF56A198FCEBCF066DB4A9605(L_0, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL);
\t\tif (!L_1)
\t\t{
\t\t\tgoto IL_0019;
\t\t}
\t}
\t{
\t\tGameObject_t76FEDD663AB33C991A9C9A23129337651094216F* L_2 = ___0_optionsPrefab;
\t\tif (Object_op_Equality_mB6120F782D83091EF56A198FCEBCF066DB4A9605(L_2, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL))
\t\t{
\t\t\tL_2 = (GameObject_t76FEDD663AB33C991A9C9A23129337651094216F*)Resources_Load_TisRuntimeObject_mD1AF6299B14F87ED1D1A6199A51480919F7C79D7_gshared(il2cpp_codegen_string_new_wrapper("optionsScreen"), Resources_Load_TisGameObject_t76FEDD663AB33C991A9C9A23129337651094216F_m496A3B1B60A28F5E0397043974B848C9157B625A_RuntimeMethod_var);
\t\t}
\t\tGameObject_t76FEDD663AB33C991A9C9A23129337651094216F* L_3;
\t\tL_3 = MenuScreenManager_Instantiate_m792DCC5C8411B311F2866C149A325B618AD01E12(__this, L_2, NULL);
\t\tif (L_3 != NULL) { Utility_DontAssociateWithAnyScene_m7F5E614627B34BF7A9A23BC4D04A92FB23D3A98B(L_3, NULL); }
\t}

IL_0019:
\t{
\t\treturn;
\t}"""
    content = replace_func_body(content, setup_opt_decl, setup_opt_body)

    # 4. Prevent LegacyMaterialTransparencyAnimator and LegacyTransparancyAnimator from caching 0.0f
    #    as m_originalValue / m_originalAlphas when a material starts at t=0 of a fade-in curve.
    old_legacy_mat_alpha = "\t\tfloat L_7 = L_6.___a;\n\t\t__this->___m_originalValue = L_7;"
    new_legacy_mat_alpha = "\t\tfloat L_7 = L_6.___a;\n\t\tif (L_7 <= 0.001f) { L_7 = 0.5f; }\n\t\t__this->___m_originalValue = L_7;"
    if "if (L_7 <= 0.001f) { L_7 = 0.5f; }" not in content:
        if old_legacy_mat_alpha not in content:
            raise RuntimeError("Could not find L_7 assignment in LegacyMaterialTransparencyAnimator_Start")
        content = content.replace(old_legacy_mat_alpha, new_legacy_mat_alpha, 1)

    old_legacy_trans_alpha = "\t\tfloat L_45 = ((L_43)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_44)))->___a;\n\t\tNullCheck(L_41);\n\t\t(L_41)->SetAt(static_cast<il2cpp_array_size_t>(L_42), (float)L_45);"
    new_legacy_trans_alpha = "\t\tfloat L_45 = ((L_43)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_44)))->___a;\n\t\tif (L_45 <= 0.001f) { L_45 = 0.5f; }\n\t\tNullCheck(L_41);\n\t\t(L_41)->SetAt(static_cast<il2cpp_array_size_t>(L_42), (float)L_45);"
    if "if (L_45 <= 0.001f) { L_45 = 0.5f; }" not in content:
        if old_legacy_trans_alpha not in content:
            raise RuntimeError("Could not find L_45 assignment in LegacyTransparancyAnimator_CacheShaderInformation")
        content = content.replace(old_legacy_trans_alpha, new_legacy_trans_alpha, 1)

    # 5. Lock Time.fixedDeltaTime to 1/60s (0.0166666675f) in MaxDeviceFrameRate.Awake so 120Hz ProMotion
    #    iPhones do not run FixedUpdate / enemy movement at 2x speed!
    max_fps_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void MaxDeviceFrameRate_Awake_mE3A38FA8B51F38CF84D3F20EFECB901273426778"
    max_fps_body = """\t{
\t\tTime_set_fixedDeltaTime_m8D8417B234CFF76AF81890D5AF67D8C54EFD189F((0.0166666675f), NULL);
\t\tBehaviour_set_enabled_mF1DCFE60EB09E0529FE9476CA804A3AA2D72B16A(__this, (bool)0, NULL);
\t\treturn;
\t}"""
    content = replace_func_body(content, max_fps_decl, max_fps_body)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__11.cpp (LoadingBootstrap + OptionsScreen Resources fallback + LegacyTransparencyAnimator alpha clamp + 60Hz FixedUpdate)")


def patch_assembly_csharp_13(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__13.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove any previous OriPort_SanitizeSceneRenderers block so re-running the script is idempotent
    render_frame_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void OriPortManualPresenter_RenderFrame_m9CADB5C9F1B1990254DE31AA31AAB8DA5F9F8052 (OriPortManualPresenter_t2F5F855B4DF012477351066DD463FB5872874118* __this, const RuntimeMethod* method) \n{"
    if render_frame_decl not in content:
        render_frame_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void OriPortManualPresenter_RenderFrame_m9CADB5C9F1B1990254DE31AA31AAB8DA5F9F8052 (OriPortManualPresenter_t2F5F855B4DF012477351066DD463FB5872874118* __this, const RuntimeMethod* method)\n{"
    if render_frame_decl not in content:
        raise RuntimeError("Could not find OriPortManualPresenter_RenderFrame definition in Assembly-CSharp__13.cpp")

    old_block_start = content.find("IL2CPP_EXTERN_C String_t* _stringLiteral57731D1C7614FDA9B9F849E36B9C6D9B7278712C;")
    rf_idx = content.find(render_frame_decl)
    if old_block_start != -1 and old_block_start < rf_idx:
        content = content[:old_block_start] + content[rf_idx:]

    # Add external declarations and a fast signature-gated in-place scene renderer & shader sanitizer:
    # 1. Preserves all 3,697 real recovered Hidden/UberShader/* shaders (those with _OriPortRecovered).
    # 2. Replaces Distance Field Text materials (_TxtTexture != null) with OriPort/DistanceFieldText in-place.
    # 3. Replaces the 103 non-recovered unlit_dummy Hidden/UberShader/* shaders (missing _OriPortRecovered)
    #    with OriPort/FallbackUnlit in-place (handling _MainTex_US_ATLAS_ST sub-sprite UV cropping,
    #    _DepthFlipScreen.y 90-deg rotation, and SCREEN_RED/SCREEN_GREEN/SCREEN_BLUE chroma-key subtraction).
    # 4. Clamps _DepthFlipScreen.x into [-100, 900] for Metal Reversed-Z.
    # 5. Disables Hidden/EarlyZWrite dummy opaque Lambert prepass renderers.
    extern_decls = """IL2CPP_EXTERN_C String_t* _stringLiteral57731D1C7614FDA9B9F849E36B9C6D9B7278712C;
IL2CPP_EXTERN_C String_t* _stringLiteral1E5A05C3CB0E65E4EC72B4E86353C4177C469AEA;
IL2CPP_EXTERN_C String_t* _stringLiteral82CBFBC9D96154286C59A7A832F44ACA59CCC81D;
IL2CPP_EXTERN_C String_t* _stringLiteral12423BE7F4613F1339F6D1EB4246E858CEF4B093;
IL2CPP_EXTERN_C String_t* _stringLiteralD14C58C1EE361C9330F36F7B5E51A6947D158C6E;
IL2CPP_EXTERN_C String_t* _stringLiteral7078454B1E5C2E624B80831BA98D6DD13E9272FD;
IL2CPP_EXTERN_C String_t* _stringLiteralCE9C589CA1C6D1CB29B40C006FAA5870083004B1;
IL2CPP_EXTERN_C const RuntimeType* Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF_0_0_0_var;
IL2CPP_EXTERN_C RuntimeClass* Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C RuntimeClass* Type_t_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR MaterialU5BU5D_t2B1D11C42DB07A4400C0535F92DBB87A2E346D3D* Renderer_get_sharedMaterials_m0B61AFD8EDA35A70C796FFB2F28BB62380051ABF (Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF* __this, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Renderer_set_enabled_m015E6D7B825528A31182F267234CC6A925F71DA8 (Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF* __this, bool ___0_value, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR Shader_tADC867D36B7876EE22427FAA2CE485105F4EE692* Material_get_shader_m8B0C11AE6F2AD7DE30AF52D3195EB716F7A71983 (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Material_set_shader_mBD3A0D9AB14DE2F7CD5F2775E9AD58E15424C171 (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, Shader_tADC867D36B7876EE22427FAA2CE485105F4EE692* ___0_value, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int32_t Material_get_renderQueue_mC427C54D2667620CBB845559DA4DA31BE166C757 (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Material_set_renderQueue_mFBB72A781DCCF0D4B85670B597788EC2D02D1C14 (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, int32_t ___0_value, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool Material_HasProperty_mC09A83B44E368A217F606DD4954FA080CC03EC6C (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, String_t* ___0_name, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* Material_GetTexture_mBA07A377A7DDD29CD53E6F687DE6D49A42C0C719 (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, String_t* ___0_name, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 Material_GetVector_mA2011D4DA2CC58003AE90DBF0802CF5EE31B014D (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, String_t* ___0_name, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Material_SetVector_m69444B8040D955821F241113446CC8713C9E12D1 (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, String_t* ___0_name, Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 ___1_value, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool String_StartsWith_mF75DBA1EB709811E711B44E26FF919C88A8E65C0 (String_t* __this, String_t* ___0_value, const RuntimeMethod* method);
IL2CPP_EXTERN_C void OriPort_UpdateTurbulenceGlobals();

static void OriPort_SanitizeSceneRenderers()
{
\tstatic bool s_init = false;
\tif (!s_init)
\t{
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF_0_0_0_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Type_t_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral1E5A05C3CB0E65E4EC72B4E86353C4177C469AEA);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral57731D1C7614FDA9B9F849E36B9C6D9B7278712C);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral82CBFBC9D96154286C59A7A832F44ACA59CCC81D);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral12423BE7F4613F1339F6D1EB4246E858CEF4B093);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteralD14C58C1EE361C9330F36F7B5E51A6947D158C6E);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral7078454B1E5C2E624B80831BA98D6DD13E9272FD);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteralCE9C589CA1C6D1CB29B40C006FAA5870083004B1);
\t\ts_init = true;
\t}
\ttry
\t{
\t\tRuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B rHandle = { reinterpret_cast<intptr_t>(Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF_0_0_0_var) };
\t\til2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
\t\tType_t* rType = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(rHandle, NULL);
\t\til2cpp_codegen_runtime_class_init_inline(Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);
\t\tObjectU5BU5D_tD4BF1BEC72A31DF6611C0B8FA3112AF128FC3F8A* objs = Object_FindObjectsOfType_m3F1266E2DA67B067B22A3105C8F86A4EECCFEC4A(rType, NULL);
\t\tif (objs == NULL) return;
\t\tint32_t count = (int32_t)(((RuntimeArray*)objs)->max_length);
\t\tuint64_t sig = (uint64_t)count;
\t\tfor (int32_t k = 0; k < count; k++)
\t\t{
\t\t\tsig = (sig * 1099511628211ULL) ^ (uint64_t)(uintptr_t)(objs->GetAt(static_cast<il2cpp_array_size_t>(k)));
\t\t}
\t\tstatic uint64_t s_lastSig = 0;
\t\tstatic int32_t s_repeatPasses = 0;
\t\tif (sig == s_lastSig && s_repeatPasses <= 0)
\t\t{
\t\t\treturn;
\t\t}
\t\tif (sig != s_lastSig)
\t\t{
\t\t\ts_lastSig = sig;
\t\t\ts_repeatPasses = 1;
\t\t}
\t\telse
\t\t{
\t\t\ts_repeatPasses--;
\t\t}
\t\tShader_tADC867D36B7876EE22427FAA2CE485105F4EE692* textShader = Shader_Find_m183AA54F78320212DDEC811592F98456898A41C5(_stringLiteral7078454B1E5C2E624B80831BA98D6DD13E9272FD, NULL);
\t\tShader_tADC867D36B7876EE22427FAA2CE485105F4EE692* fallbackShader = Shader_Find_m183AA54F78320212DDEC811592F98456898A41C5(_stringLiteralD14C58C1EE361C9330F36F7B5E51A6947D158C6E, NULL);
\t\tfor (int32_t i = 0; i < count; i++)
\t\t{
\t\t\tObject_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C* obj = objs->GetAt(static_cast<il2cpp_array_size_t>(i));
\t\t\tif (obj == NULL) continue;
\t\t\tRenderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF* ren = (Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF*)CastclassClass((RuntimeObject*)obj, Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF_il2cpp_TypeInfo_var);
\t\t\tif (ren == NULL || Object_op_Equality_mB6120F782D83091EF56A198FCEBCF066DB4A9605(ren, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL)) continue;
\t\t\tMaterialU5BU5D_t2B1D11C42DB07A4400C0535F92DBB87A2E346D3D* mats = Renderer_get_sharedMaterials_m0B61AFD8EDA35A70C796FFB2F28BB62380051ABF(ren, NULL);
\t\t\tif (mats == NULL) continue;
\t\t\tint32_t mCount = (int32_t)(((RuntimeArray*)mats)->max_length);
\t\t\tfor (int32_t j = 0; j < mCount; j++)
\t\t\t{
\t\t\t\tMaterial_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* mat = mats->GetAt(static_cast<il2cpp_array_size_t>(j));
\t\t\t\tif (mat == NULL || Object_op_Equality_mB6120F782D83091EF56A198FCEBCF066DB4A9605(mat, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL)) continue;
\t\t\t\tShader_tADC867D36B7876EE22427FAA2CE485105F4EE692* sh = Material_get_shader_m8B0C11AE6F2AD7DE30AF52D3195EB716F7A71983(mat, NULL);
\t\t\t\tif (sh == NULL || Object_op_Equality_mB6120F782D83091EF56A198FCEBCF066DB4A9605(sh, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL)) continue;
\t\t\t\tString_t* shName = Object_get_name_mAC2F6B897CF1303BA4249B4CB55271AFACBB6392(sh, NULL);
\t\t\t\tif (shName != NULL)
\t\t\t\t{
\t\t\t\t\tif (String_op_Equality_m030E1B219352228970A076136E455C4E568C02C1(shName, _stringLiteral1E5A05C3CB0E65E4EC72B4E86353C4177C469AEA, NULL))
\t\t\t\t\t{
\t\t\t\t\t\tRenderer_set_enabled_m015E6D7B825528A31182F267234CC6A925F71DA8(ren, (bool)0, NULL);
\t\t\t\t\t\tcontinue;
\t\t\t\t\t}
\t\t\t\t\tif (String_StartsWith_mF75DBA1EB709811E711B44E26FF919C88A8E65C0(shName, _stringLiteral82CBFBC9D96154286C59A7A832F44ACA59CCC81D, NULL))
\t\t\t\t\t{
\t\t\t\t\t\tint32_t rq = Material_get_renderQueue_mC427C54D2667620CBB845559DA4DA31BE166C757(mat, NULL);
\t\t\t\t\t\tbool isText = false;
\t\t\t\t\t\tif (Material_HasProperty_mC09A83B44E368A217F606DD4954FA080CC03EC6C(mat, _stringLiteral12423BE7F4613F1339F6D1EB4246E858CEF4B093, NULL))
\t\t\t\t\t\t{
\t\t\t\t\t\t\tTexture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* txtTex = Material_GetTexture_mBA07A377A7DDD29CD53E6F687DE6D49A42C0C719(mat, _stringLiteral12423BE7F4613F1339F6D1EB4246E858CEF4B093, NULL);
\t\t\t\t\t\t\tif (txtTex != NULL && Object_op_Inequality_mD0BE578448EAA61948F25C32F8DD55AB1F778602(txtTex, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL))
\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\tisText = true;
\t\t\t\t\t\t\t}
\t\t\t\t\t\t}
\t\t\t\t\t\tif (isText && textShader != NULL && Object_op_Inequality_mD0BE578448EAA61948F25C32F8DD55AB1F778602(textShader, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL))
\t\t\t\t\t\t{
\t\t\t\t\t\t\tMaterial_set_shader_mBD3A0D9AB14DE2F7CD5F2775E9AD58E15424C171(mat, textShader, NULL);
\t\t\t\t\t\t\tMaterial_set_renderQueue_mFBB72A781DCCF0D4B85670B597788EC2D02D1C14(mat, rq, NULL);
\t\t\t\t\t\t}
\t\t\t\t\t\telse if (!Material_HasProperty_mC09A83B44E368A217F606DD4954FA080CC03EC6C(mat, _stringLiteralCE9C589CA1C6D1CB29B40C006FAA5870083004B1, NULL))
\t\t\t\t\t\t{
\t\t\t\t\t\t\tif (fallbackShader != NULL && Object_op_Inequality_mD0BE578448EAA61948F25C32F8DD55AB1F778602(fallbackShader, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL))
\t\t\t\t\t\t\t{
\t\t\t\t\t\t\t\tMaterial_set_shader_mBD3A0D9AB14DE2F7CD5F2775E9AD58E15424C171(mat, fallbackShader, NULL);
\t\t\t\t\t\t\t\tMaterial_set_renderQueue_mFBB72A781DCCF0D4B85670B597788EC2D02D1C14(mat, rq, NULL);
\t\t\t\t\t\t\t}
\t\t\t\t\t\t}
\t\t\t\t\t}
\t\t\t\t}
\t\t\t\tif (Material_HasProperty_mC09A83B44E368A217F606DD4954FA080CC03EC6C(mat, _stringLiteral57731D1C7614FDA9B9F849E36B9C6D9B7278712C, NULL))
\t\t\t\t{
\t\t\t\t\tVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 df = Material_GetVector_mA2011D4DA2CC58003AE90DBF0802CF5EE31B014D(mat, _stringLiteral57731D1C7614FDA9B9F849E36B9C6D9B7278712C, NULL);
\t\t\t\t\tif (df.___x < -100.0f || df.___x > 900.0f)
\t\t\t\t\t{
\t\t\t\t\t\tdf.___x = 0.0f;
\t\t\t\t\t\tMaterial_SetVector_m69444B8040D955821F241113446CC8713C9E12D1(mat, _stringLiteral57731D1C7614FDA9B9F849E36B9C6D9B7278712C, df, NULL);
\t\t\t\t\t}
\t\t\t\t}
\t\t\t}
\t\t}
\t}
\tcatch (Il2CppExceptionWrapper&)
\t{
\t}
}
"""
    content = content.replace(render_frame_decl, extern_decls + render_frame_decl, 1)

    # 1. In OriPortManualPresenter_RenderFrame:
    #    - Periodically run OriPort_SanitizeSceneRenderers() (every 15 frames; fast-exits in 2us when scene is unchanged)
    #    - Call OriPortManualPresenter_UpdateAlphaGrab(__this, V_2, V_3, NULL) after Camera.Render()
    #    - Do NOT call OriPortManualPresenter_RenderUserInterface (UberPostProcess.DoCompatibilityPost already renders UI cameras, and RenderUserInterface logs "Tag: UICamera is not defined.")
    old_render_call = """\t\t\t\tShader_SetGlobalFloat_m8AA7A4D7D73914A00D9207D78621EDDF70602FB0(_stringLiteral682BF2EFA52E75C110EBBFF64FA09D54B09DA240, (-1.0f), NULL);
\t\t\t\tOriPortManualPresenter_set_IsRenderingPresentedFrame_m1760BA79F65488022AE1A93714CC89A44E71424E_inline((bool)1, NULL);
\t\t\t\tCamera_tA92CC927D7439999BC82DBEDC0AA45B470F9E184* L_71 = V_1;
\t\t\t\tNullCheck(L_71);
\t\t\t\tCamera_Render_m6089001EB6710DA9A21C87185D65922F13A24509(L_71, NULL);
\t\t\t\tgoto IL_01b7;"""

    new_render_call = """\t\t\t\tstatic int32_t s_sanitizeCounter = 0;
\t\t\t\tif ((s_sanitizeCounter++ % 15) == 0)
\t\t\t\t{
\t\t\t\t\tOriPort_SanitizeSceneRenderers();
\t\t\t\t}
\t\t\t\tShader_SetGlobalFloat_m8AA7A4D7D73914A00D9207D78621EDDF70602FB0(_stringLiteral682BF2EFA52E75C110EBBFF64FA09D54B09DA240, (-1.0f), NULL);
\t\t\t\tOriPortManualPresenter_set_IsRenderingPresentedFrame_m1760BA79F65488022AE1A93714CC89A44E71424E_inline((bool)1, NULL);
\t\t\t\tCamera_tA92CC927D7439999BC82DBEDC0AA45B470F9E184* L_71 = V_1;
\t\t\t\tNullCheck(L_71);
\t\t\t\tCamera_Render_m6089001EB6710DA9A21C87185D65922F13A24509(L_71, NULL);
\t\t\t\ttry
\t\t\t\t{
\t\t\t\t\tOriPortManualPresenter_UpdateAlphaGrab_m6D5C8A797031A3CAABF1F73E449DA1A147570CEF(__this, V_2, V_3, NULL);
\t\t\t\t}
\t\t\t\tcatch (Il2CppExceptionWrapper&)
\t\t\t\t{
\t\t\t\t}
\t\t\t\tgoto IL_01b7;"""

    prev_render_call = new_render_call
    new_render_call = (
        "\t\t\t\tstatic int32_t s_sanitizeCounter = 0;\n"
        "\t\t\t\tif ((s_sanitizeCounter++ % 15) == 0)\n"
        "\t\t\t\t{\n"
        "\t\t\t\t\tOriPort_SanitizeSceneRenderers();\n"
        "\t\t\t\t}\n"
        "\t\t\t\tOriPort_UpdateTurbulenceGlobals();\n"
        "\t\t\t\tShader_SetGlobalFloat_m8AA7A4D7D73914A00D9207D78621EDDF70602FB0(_stringLiteral682BF2EFA52E75C110EBBFF64FA09D54B09DA240, (-1.0f), NULL);\n"
        "\t\t\t\tOriPortManualPresenter_set_IsRenderingPresentedFrame_m1760BA79F65488022AE1A93714CC89A44E71424E_inline((bool)1, NULL);\n"
        "\t\t\t\tCamera_tA92CC927D7439999BC82DBEDC0AA45B470F9E184* L_71 = V_1;\n"
        "\t\t\t\tNullCheck(L_71);\n"
        "\t\t\t\tCamera_Render_m6089001EB6710DA9A21C87185D65922F13A24509(L_71, NULL);\n"
        "\t\t\t\tgoto IL_01b7;"
    )
    if prev_render_call in content:
        content = content.replace(prev_render_call, new_render_call, 1)
    elif "OriPort_UpdateTurbulenceGlobals();" not in content.split(render_frame_decl, 1)[1]:
        if old_render_call not in content:
            raise RuntimeError("Could not find Camera_Render block in OriPortManualPresenter_RenderFrame")
        content = content.replace(old_render_call, new_render_call, 1)

    # 2. Wrap OriPortManualPresenter_RenderFrame call inside U3CStartU3Ed__13_MoveNext in a try/catch
    #    so that if any single frame ever throws a managed exception during rendering, the
    #    WaitForEndOfFrame presenter coroutine never terminates!
    old_movenext_call = """IL_003d:
\t{
\t\t__this->___U3CU3E1__state = (-1);
\t\tOriPortManualPresenter_t2F5F855B4DF012477351066DD463FB5872874118* L_7 = V_1;
\t\tNullCheck(L_7);
\t\tOriPortManualPresenter_RenderFrame_m9CADB5C9F1B1990254DE31AA31AAB8DA5F9F8052(L_7, NULL);
\t\tgoto IL_0029;
\t}"""

    new_movenext_call = """IL_003d:
\t{
\t\t__this->___U3CU3E1__state = (-1);
\t\tOriPortManualPresenter_t2F5F855B4DF012477351066DD463FB5872874118* L_7 = V_1;
\t\tif (L_7 != NULL)
\t\t{
\t\t\ttry
\t\t\t{
\t\t\t\tOriPortManualPresenter_RenderFrame_m9CADB5C9F1B1990254DE31AA31AAB8DA5F9F8052(L_7, NULL);
\t\t\t}
\t\t\tcatch (Il2CppExceptionWrapper&)
\t\t\t{
\t\t\t}
\t\t}
\t\tgoto IL_0029;
\t}"""

    if "if (L_7 != NULL)" not in content:
        if old_movenext_call not in content:
            raise RuntimeError("Could not find IL_003d block in U3CStartU3Ed__13_MoveNext")
        content = content.replace(old_movenext_call, new_movenext_call, 1)

    # 3. Fix GUI.depth in OriPortManualPresenter_OnGUI and hide OriPortTouchControls (user plays with a gamepad)
    on_gui_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void OriPortManualPresenter_OnGUI_m797B8337761723FC6A2D02EDAF956B10ED279B12"
    on_gui_body = """\tstatic bool s_Il2CppMethodInitialized;
\tif (!s_Il2CppMethodInitialized)
\t{
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&GUI_tA9CDB3D69DB13D51AD83ABDB587EF95947EC2D2A_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);
\t\ts_Il2CppMethodInitialized = true;
\t}
\t{
\t\tRenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* L_0 = __this->___m_frame;
\t\til2cpp_codegen_runtime_class_init_inline(Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);
\t\tbool L_1;
\t\tL_1 = Object_op_Equality_mB6120F782D83091EF56A198FCEBCF066DB4A9605(L_0, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL);
\t\tif (L_1)
\t\t{
\t\t\tgoto IL_0060;
\t\t}
\t}
\t{
\t\tEvent_tEBC6F24B56CE22B9C9AD1AC6C24A6B83BC3860CB* L_2;
\t\tL_2 = Event_get_current_mBD7135E10C392EAD61AC0A0D2489EF758C8A3FAD(NULL);
\t\tNullCheck(L_2);
\t\tint32_t L_3;
\t\tL_3 = Event_get_type_m8A825D6DA432B967DAA3E22E5C8571620A75F8A8(L_2, NULL);
\t\tif ((!(((uint32_t)L_3) == ((uint32_t)7))))
\t\t{
\t\t\tgoto IL_0060;
\t\t}
\t}
\t{
\t\til2cpp_codegen_runtime_class_init_inline(GUI_tA9CDB3D69DB13D51AD83ABDB587EF95947EC2D2A_il2cpp_TypeInfo_var);
\t\tGUI_set_depth_m37E8C151AD6D1B28DDFABB64A0974398AA8EC44E(((int32_t)1000), NULL);
\t\tMatrix4x4_tDB70CF134A14BA38190C59AA700BCE10E2AED3E6 L_4;
\t\tL_4 = GUI_get_matrix_m3CA02DED0598EE32BD9E66CA533A78EFB0A246FC(NULL);
\t\tColor_tD001788D726C3A7F1379BEED0260B9591F440C1F L_5;
\t\tL_5 = GUI_get_color_m15488B4AD785D10DEB5C66398D0FA9A0C0EA7ABB(NULL);
\t\tMatrix4x4_tDB70CF134A14BA38190C59AA700BCE10E2AED3E6 L_6;
\t\tL_6 = Matrix4x4_get_identity_m6568A73831F3E2D587420D20FF423959D7D8AB56_inline(NULL);
\t\tGUI_set_matrix_m7759FEC96FBCB97E02B1BA44D2EC1B3FEEFA257F(L_6, NULL);
\t\tColor_tD001788D726C3A7F1379BEED0260B9591F440C1F L_7;
\t\tL_7 = Color_get_white_m068F5AF879B0FCA584E3693F762EA41BB65532C6_inline(NULL);
\t\tGUI_set_color_mA44927D3F2ACB1E228815F10042A6F62B7645648(L_7, NULL);
\t\tRect_tA04E0F8A1830E767F40FB27ECD8D309303571F0D L_8 = __this->___m_displayRect;
\t\tRenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* L_9 = __this->___m_frame;
\t\tGUI_DrawTexture_m05F173ECE6F2D78FFBDEB0052EB58AC2B5A7420E(L_8, L_9, 0, (bool)0, NULL);
\t\tGUI_set_color_mA44927D3F2ACB1E228815F10042A6F62B7645648(L_5, NULL);
\t\tGUI_set_matrix_m7759FEC96FBCB97E02B1BA44D2EC1B3FEEFA257F(L_4, NULL);
\t}

IL_0060:
\t{
\t\treturn;
\t}"""
    content = replace_func_body(content, on_gui_decl, on_gui_body)

    # 4. Hide OriPortTouchControls completely (return false for GameplayControlsEnabled)
    touch_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool OriPortTouchControls_get_GameplayControlsEnabled_mF19030CD53AA9F354B8004DF880315F11D19BFA5"
    touch_body = "\treturn (bool)0;"
    content = replace_func_body(content, touch_decl, touch_body)

    # 5. Make OriPortShaderFallback_IsRecoveredShader return true, PatchLoadedRenderers no-op,
    #    and stop U3CStartU3Ed__4_MoveNext coroutine immediately so it never allocates WaitForSeconds(0.25f) forever!
    is_rec_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool OriPortShaderFallback_IsRecoveredShader_m1A7E0555FB0BC694339005AED36D901FFBE886A4"
    is_rec_body = "\treturn (bool)1;"
    content = replace_func_body(content, is_rec_decl, is_rec_body)

    patch_renderers_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void OriPortShaderFallback_PatchLoadedRenderers_m6207097F5CCA64E7C293C7E24CD958FAEC3B8444"
    patch_renderers_body = "\treturn;"
    content = replace_func_body(content, patch_renderers_decl, patch_renderers_body)

    sf_movenext_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool U3CStartU3Ed__4_MoveNext_m2BF10473120F4BA707021D0DB37468B3C63A0289"
    sf_movenext_body = "\treturn (bool)0;"
    content = replace_func_body(content, sf_movenext_decl, sf_movenext_body)

    # 6. Stub OriPortRuntimeDiagnostics completely so it never runs ProfilerRecorder queries, 512-float array sorts,
    #    42-string CSV formatting, or synchronous StreamWriter.Flush() on the main thread (eliminates audio crackling!)
    diag_stubs = [
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void OriPortRuntimeDiagnostics_Install_mE2919656F0C03CA9A485DFCE10032987B0DC96EF", "\treturn;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void OriPortRuntimeDiagnostics_Awake_m8DE05A48E677F462DECE5945E0A13B2408BFCA73", "\treturn;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void OriPortRuntimeDiagnostics_Update_mF6B737AB9052DBED28785F140CD6E66DF8D74E1A", "\treturn;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void OriPortRuntimeDiagnostics_LateUpdate_mE10120DC1FDD78D8915AB1D2829DB999037DD03C", "\treturn;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int64_t OriPortRuntimeDiagnostics_BeginDamage_mCDC816823F666832BBBC02DE1FF9538EC388C92E", "\treturn 0;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int64_t OriPortRuntimeDiagnostics_BeginAttackPhase_m86422FA63A1D8968B0D4F54FFCBBDB96BBB419CF", "\treturn 0;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void OriPortRuntimeDiagnostics_EndProjectileSpawn_m5754329BC94196904413A118AF602E991C8E0303", "\treturn;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void OriPortRuntimeDiagnostics_EndProjectileImpact_m9F127212AD6CDFF35A0FC569E88595B89FB2DCC7", "\treturn;"),
        ("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void OriPortRuntimeDiagnostics_EndDamage_mB50B0656EC05D41FC330BBBE930378C69E8CAB60", "\treturn;"),
    ]
    for decl, body in diag_stubs:
        if decl in content:
            content = replace_func_body(content, decl, body)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__13.cpp (Preserved 3697 recovered UberShaders + FallbackUnlit for 103 unlit_dummy shaders + disabled OriPortRuntimeDiagnostics stalls)")


def patch_assembly_csharp_17(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__17.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # In SaveSlotUI_Awake, ScreenshotB (screenshotReflection) has localScale.y = -4.309868 (upside down)
    # and sortingOrder = 3594 (above Screenshot's 3167). Applying the opaque circular mesh to ScreenshotB
    # covers Screenshot with an upside-down preview! Disable ScreenshotB's Renderer instead.
    extern_ren = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Renderer_set_enabled_m015E6D7B825528A31182F267234CC6A925F71DA8 (Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF* __this, bool ___0_value, const RuntimeMethod* method);\n"
    awake_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void SaveSlotUI_Awake_mBC316003758B1A8BDF200E118164AABA0F5B8523"
    if extern_ren not in content:
        content = content.replace(awake_decl, extern_ren + awake_decl, 1)

    old_refl = """\t\tRenderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF* L_1 = __this->___ScreenshotB;
\t\tSaveSlotUI_ApplyCircularScreenshotMesh_m0A61BF51D11D6B59721D164D32149EC10EAD0EB9(L_1, NULL);"""
    new_refl = """\t\tRenderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF* L_1 = __this->___ScreenshotB;
\t\tif (L_1 != NULL) { Renderer_set_enabled_m015E6D7B825528A31182F267234CC6A925F71DA8(L_1, (bool)0, NULL); }"""
    if "Renderer_set_enabled_m015E6D7B825528A31182F267234CC6A925F71DA8(L_1, (bool)0, NULL);" not in content:
        if old_refl not in content:
            raise RuntimeError("Could not find ScreenshotB ApplyCircularScreenshotMesh in SaveSlotUI_Awake (Assembly-CSharp__17.cpp)")
        content = content.replace(old_refl, new_refl, 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__17.cpp (SaveSlotUI.Awake disables upside-down ScreenshotB reflection overlay)")


def patch_assembly_csharp_21(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__21.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    extern_snap = "IL2CPP_EXTERN_C void OriPort_SnapCameraToCurrentCharacter();\n"
    sein_after_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void SeinPlaceholder_AfterLoadingFromMasterFinishedAfterInstantiation_mE35B1CC48FEB0E9B5FAF70356BC9EB9AA4B2448C"
    if extern_snap not in content:
        content = content.replace(sein_after_decl, extern_snap + sein_after_decl, 1)

    old_il_00cf = """\t\tGameController_SetupGameplay_m4E0B29AA5DFC4661545DD09039FB67D56757BC06(L_24, L_25, L_26, NULL);
\t}

IL_00cf:
\t{
\t\treturn;
\t}"""
    new_il_00cf = """\t\tGameController_SetupGameplay_m4E0B29AA5DFC4661545DD09039FB67D56757BC06(L_24, L_25, L_26, NULL);
\t}

IL_00cf:
\t{
\t\tOriPort_SnapCameraToCurrentCharacter();
\t\treturn;
\t}"""
    if "OriPort_SnapCameraToCurrentCharacter();" not in content.split(sein_after_decl, 1)[1]:
        if old_il_00cf not in content:
            raise RuntimeError("Could not find IL_00cf in SeinPlaceholder_AfterLoadingFromMasterFinishedAfterInstantiation")
        content = content.replace(old_il_00cf, new_il_00cf, 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__21.cpp (SeinPlaceholder snaps GameplayCamera to Ori after spawn)")


def patch_assembly_csharp_27(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__27.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Clamp L_15 (z) in UberShaderRenderQueue_SetRenderQueueExplicit so _DepthFlipScreen.x stays in [-100, 900]
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

    # 2. Make UberShaderPrewarmer.WarmProgress return 1.0f when prewarming is skipped (Instance == null)
    warm_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR float UberShaderPrewarmer_get_WarmProgress_mF0F575F8E3E8B5ECDA409B501D76D3CEB697B2A7"
    warm_body = "\treturn 1.0f;"
    content = replace_func_body(content, warm_decl, warm_body)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__27.cpp (UberShaderRenderQueue _DepthFlipScreen.x clamp + WarmProgress -> 1.0f)")


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

    # 3. Fix Sound.SoundListenerPosition so cutscene camera positions are used for 3D audio attenuation
    old_listener = (
        "IL_001a:\n"
        "\t{\n"
        "\t\tGameplayCamera_t0939DE616725B1ED6EEBFB571FAFFE64C578EF00* L_4 = ((Cameras_t7935DA243CF368EB505A27E50005C968D54D5A90_StaticFields*)il2cpp_codegen_static_fields_for(Cameras_t7935DA243CF368EB505A27E50005C968D54D5A90_il2cpp_TypeInfo_var))->___Current;\n"
        "\t\tNullCheck(L_4);\n"
        "\t\tCameraTarget_t078491F9A4589091B931D7C3651E01DA95C55FEC* L_5 = L_4->___CameraTarget;\n"
        "\t\tNullCheck(L_5);\n"
        "\t\tVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 L_6 = L_5->___TargetPosition;\n"
        "\t\treturn L_6;\n"
        "\t}\n\n"
        "IL_002a:\n"
        "\t{\n"
        "\t\tRuntimeObject* L_7 = ((Characters_tF59E7350484B625A1E1F9237B1CD79599AA4310B_StaticFields*)il2cpp_codegen_static_fields_for(Characters_tF59E7350484B625A1E1F9237B1CD79599AA4310B_il2cpp_TypeInfo_var))->___Current;\n"
        "\t\tNullCheck(L_7);\n"
        "\t\tVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 L_8;\n"
        "\t\tL_8 = InterfaceFuncInvoker0< Vector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 >::Invoke(0, ICharacter_tFA100B2676DEB2AD3DD3495D74ECB1C320D3FC3F_il2cpp_TypeInfo_var, L_7);\n"
        "\t\treturn L_8;\n"
        "\t}"
    )
    new_listener = (
        "IL_001a:\n"
        "\t{\n"
        "\t\tGameplayCamera_t0939DE616725B1ED6EEBFB571FAFFE64C578EF00* L_4 = ((Cameras_t7935DA243CF368EB505A27E50005C968D54D5A90_StaticFields*)il2cpp_codegen_static_fields_for(Cameras_t7935DA243CF368EB505A27E50005C968D54D5A90_il2cpp_TypeInfo_var))->___Current;\n"
        "\t\tif (L_4 != NULL) { return L_4->___CameraPositionForSampling; }\n"
        "\t\tVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 zeroPos = { 0.0f, 0.0f, 0.0f };\n"
        "\t\treturn zeroPos;\n"
        "\t}\n\n"
        "IL_002a:\n"
        "\t{\n"
        "\t\tRuntimeObject* L_7 = ((Characters_tF59E7350484B625A1E1F9237B1CD79599AA4310B_StaticFields*)il2cpp_codegen_static_fields_for(Characters_tF59E7350484B625A1E1F9237B1CD79599AA4310B_il2cpp_TypeInfo_var))->___Current;\n"
        "\t\tNullCheck(L_7);\n"
        "\t\tVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 L_8;\n"
        "\t\tL_8 = InterfaceFuncInvoker0< Vector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 >::Invoke(0, ICharacter_tFA100B2676DEB2AD3DD3495D74ECB1C320D3FC3F_il2cpp_TypeInfo_var, L_7);\n"
        "\t\tGameplayCamera_t0939DE616725B1ED6EEBFB571FAFFE64C578EF00* cam = ((Cameras_t7935DA243CF368EB505A27E50005C968D54D5A90_StaticFields*)il2cpp_codegen_static_fields_for(Cameras_t7935DA243CF368EB505A27E50005C968D54D5A90_il2cpp_TypeInfo_var))->___Current;\n"
        "\t\tif (cam != NULL)\n"
        "\t\t{\n"
        "\t\t\tVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 camPos = cam->___CameraPositionForSampling;\n"
        "\t\t\tfloat dx = camPos.___x - L_8.___x;\n"
        "\t\t\tfloat dy = camPos.___y - L_8.___y;\n"
        "\t\t\tif ((dx * dx + dy * dy) > 400.0f) { return camPos; }\n"
        "\t\t}\n"
        "\t\treturn L_8;\n"
        "\t}"
    )
    if "L_4->___CameraPositionForSampling" not in content:
        if old_listener not in content:
            raise RuntimeError("Could not find Sound_get_SoundListenerPosition block in Assembly-CSharp__29.cpp")
        content = content.replace(old_listener, new_listener, 1)

    # 4. Fix Sound.Play distance culling so 2D sounds at (0,0,0) and cutscene sounds near the moving camera are never culled
    old_cull = (
        "IL_0048:\n"
        "\t{\n"
        "\t\tSoundSize_t03D7804D5DBAE76CE9CC63D30CBE747FDD3846C3* L_12 = ___3_soundSize;\n"
        "\t\tNullCheck(L_12);\n"
        "\t\tfloat L_13 = L_12->___Radius;\n"
        "\t\tSoundSize_t03D7804D5DBAE76CE9CC63D30CBE747FDD3846C3* L_14 = ___3_soundSize;\n"
        "\t\tNullCheck(L_14);\n"
        "\t\tfloat L_15 = L_14->___FalloffMargin;\n"
        "\t\tV_0 = ((float)il2cpp_codegen_add(L_13, L_15));\n"
        "\t\tGameplayCamera_t0939DE616725B1ED6EEBFB571FAFFE64C578EF00* L_16 = ((Cameras_t7935DA243CF368EB505A27E50005C968D54D5A90_StaticFields*)il2cpp_codegen_static_fields_for(Cameras_t7935DA243CF368EB505A27E50005C968D54D5A90_il2cpp_TypeInfo_var))->___Current;\n"
        "\t\tNullCheck(L_16);\n"
        "\t\tTransform_tB27202C6F4E36D225EE28A13E4D662BF99785DB1* L_17;\n"
        "\t\tL_17 = GameplayCamera_get_Target_mB590E93626C28F1E1C40BA4A66D970851B571A03(L_16, NULL);\n"
        "\t\til2cpp_codegen_runtime_class_init_inline(Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);\n"
        "\t\tbool L_18;\n"
        "\t\tL_18 = Object_op_Implicit_m93896EF7D68FA113C42D3FE2BC6F661FC7EF514A(L_17, NULL);\n"
        "\t\tif (!L_18)\n"
        "\t\t{\n"
        "\t\t\tgoto IL_008b;\n"
        "\t\t}\n"
        "\t}\n"
        "\t{\n"
        "\t\tfloat L_19 = V_0;\n"
        "\t\tfloat L_20 = V_0;\n"
        "\t\tVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 L_21 = ___1_position;\n"
        "\t\tGameplayCamera_t0939DE616725B1ED6EEBFB571FAFFE64C578EF00* L_22 = ((Cameras_t7935DA243CF368EB505A27E50005C968D54D5A90_StaticFields*)il2cpp_codegen_static_fields_for(Cameras_t7935DA243CF368EB505A27E50005C968D54D5A90_il2cpp_TypeInfo_var))->___Current;\n"
        "\t\tNullCheck(L_22);\n"
        "\t\tTransform_tB27202C6F4E36D225EE28A13E4D662BF99785DB1* L_23;\n"
        "\t\tL_23 = GameplayCamera_get_Target_mB590E93626C28F1E1C40BA4A66D970851B571A03(L_22, NULL);\n"
        "\t\tNullCheck(L_23);\n"
        "\t\tVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 L_24;\n"
        "\t\tL_24 = Transform_get_position_m69CD5FA214FDAE7BB701552943674846C220FDE1(L_23, NULL);\n"
        "\t\tVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 L_25;\n"
        "\t\tL_25 = Vector3_op_Subtraction_mE42023FF80067CB44A1D4A27EB7CF2B24CABB828_inline(L_21, L_24, NULL);\n"
        "\t\tV_1 = L_25;\n"
        "\t\tfloat L_26;\n"
        "\t\tL_26 = Vector3_get_sqrMagnitude_m43C27DEC47C4811FB30AB474FF2131A963B66FC8_inline((&V_1), NULL);\n"
        "\t\tif ((!(((float)((float)il2cpp_codegen_multiply(L_19, L_20))) < ((float)L_26))))\n"
        "\t\t{\n"
        "\t\t\tgoto IL_008b;\n"
        "\t\t}\n"
        "\t}"
    )
    new_cull = (
        "IL_0048:\n"
        "\t{\n"
        "\t\tif (___1_position.___x == 0.0f && ___1_position.___y == 0.0f && ___1_position.___z == 0.0f)\n"
        "\t\t{\n"
        "\t\t\tgoto IL_008b;\n"
        "\t\t}\n"
        "\t\tSoundSize_t03D7804D5DBAE76CE9CC63D30CBE747FDD3846C3* L_12 = ___3_soundSize;\n"
        "\t\tNullCheck(L_12);\n"
        "\t\tfloat L_13 = L_12->___Radius;\n"
        "\t\tSoundSize_t03D7804D5DBAE76CE9CC63D30CBE747FDD3846C3* L_14 = ___3_soundSize;\n"
        "\t\tNullCheck(L_14);\n"
        "\t\tfloat L_15 = L_14->___FalloffMargin;\n"
        "\t\tV_0 = ((float)il2cpp_codegen_add(L_13, L_15));\n"
        "\t\tfloat L_19 = V_0;\n"
        "\t\tfloat L_20 = V_0;\n"
        "\t\tVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 L_21 = ___1_position;\n"
        "\t\tVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 L_24 = Sound_get_SoundListenerPosition_mFFE8C6DE8589D69CD2629EF49D7F0E3DDBDEBB41(NULL);\n"
        "\t\tVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 L_25;\n"
        "\t\tL_25 = Vector3_op_Subtraction_mE42023FF80067CB44A1D4A27EB7CF2B24CABB828_inline(L_21, L_24, NULL);\n"
        "\t\tV_1 = L_25;\n"
        "\t\tfloat L_26;\n"
        "\t\tL_26 = Vector3_get_sqrMagnitude_m43C27DEC47C4811FB30AB474FF2131A963B66FC8_inline((&V_1), NULL);\n"
        "\t\tif ((!(((float)((float)il2cpp_codegen_multiply(L_19, L_20))) < ((float)L_26))))\n"
        "\t\t{\n"
        "\t\t\tgoto IL_008b;\n"
        "\t\t}\n"
        "\t}"
    )
    if "___1_position.___x == 0.0f && ___1_position.___y == 0.0f" not in content:
        if old_cull not in content:
            raise RuntimeError("Could not find IL_0048 block in Sound_Play (Assembly-CSharp__29.cpp)")
        content = content.replace(old_cull, new_cull, 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__29.cpp (iOS MFi / GameSir controller support + Cutscene 3D/2D audio listener & culling fixes)")


def patch_assembly_csharp_23(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__23.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Start pooled SoundPlayers at volume 0.0f instead of 1.0f in OnPoolSpawned
    old_pool_vol = (
        "\t\tAudioSource_t871AC2272F896738252F04EE949AEF5B241D3299* L_4 = __this->___m_audioSource;\n"
        "\t\tNullCheck(L_4);\n"
        "\t\tAudioSource_set_volume_mD902BBDBBDE0E3C148609BF3C05096148E90F2C0(L_4, (1.0f), NULL);"
    )
    new_pool_vol = (
        "\t\tAudioSource_t871AC2272F896738252F04EE949AEF5B241D3299* L_4 = __this->___m_audioSource;\n"
        "\t\tNullCheck(L_4);\n"
        "\t\tAudioSource_set_volume_mD902BBDBBDE0E3C148609BF3C05096148E90F2C0(L_4, (0.0f), NULL);"
    )
    if old_pool_vol in content:
        content = content.replace(old_pool_vol, new_pool_vol, 1)

    # 2. Prevent SoundPlayer.Update from seeking (AudioSource.set_time) mid-playback on compressed Vorbis streams
    #    after TimeIsScaled transitions, which causes loud synthetic clicking/crackling on iOS!
    old_timescale_seek = (
        "\t{\n"
        "\t\t__this->___m_timeScaleChanged = (bool)0;\n"
        "\t\tAudioSource_t871AC2272F896738252F04EE949AEF5B241D3299* L_20 = __this->___m_audioSource;"
    )
    new_timescale_seek = (
        "\t{\n"
        "\t\t__this->___m_timeScaleChanged = (bool)0;\n"
        "\t\tgoto IL_0130;\n"
        "\t\tAudioSource_t871AC2272F896738252F04EE949AEF5B241D3299* L_20 = __this->___m_audioSource;"
    )
    if "__this->___m_timeScaleChanged = (bool)0;\n\t\tgoto IL_0130;" not in content:
        if old_timescale_seek not in content:
            raise RuntimeError("Could not find m_timeScaleChanged block in SoundPlayer_Update (Assembly-CSharp__23.cpp)")
        content = content.replace(old_timescale_seek, new_timescale_seek, 1)

    # 3. In SoundPlayer.UpdateVolumeProperties, if SoundSize is null or the sound is spawned at (0,0,0) (2D / cutscene sound),
    #    jump to IL_0111 so SoundType volume multipliers and AudioSource.volume = V_1 are still applied!
    old_vol_props = (
        "\t\tSoundSize_t03D7804D5DBAE76CE9CC63D30CBE747FDD3846C3* L_7 = __this->___SoundSize;\n"
        "\t\tif (L_7)\n"
        "\t\t{\n"
        "\t\t\tgoto IL_003a;\n"
        "\t\t}\n"
        "\t}\n"
        "\t{\n"
        "\t\treturn;\n"
        "\t}"
    )
    new_vol_props = (
        "\t\tif (L_2.___x == 0.0f && L_2.___y == 0.0f && L_2.___z == 0.0f)\n"
        "\t\t{\n"
        "\t\t\tgoto IL_0111;\n"
        "\t\t}\n"
        "\t\tSoundSize_t03D7804D5DBAE76CE9CC63D30CBE747FDD3846C3* L_7 = __this->___SoundSize;\n"
        "\t\tif (L_7)\n"
        "\t\t{\n"
        "\t\t\tgoto IL_003a;\n"
        "\t\t}\n"
        "\t}\n"
        "\t{\n"
        "\t\tgoto IL_0111;\n"
        "\t}"
    )
    if "if (L_2.___x == 0.0f && L_2.___y == 0.0f && L_2.___z == 0.0f)" not in content:
        if old_vol_props not in content:
            raise RuntimeError("Could not find SoundSize check in SoundPlayer_UpdateVolumeProperties (Assembly-CSharp__23.cpp)")
        content = content.replace(old_vol_props, new_vol_props, 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__23.cpp (SoundPlayer volume init + Vorbis seek crackle fix + 2D/cutscene sound attenuation fix)")


def patch_assembly_csharp_25(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__25.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. In TransparencyAnimator+RendererData..ctor, when a material's initial color alpha is <= 0.001f (e.g. at t=0 of a
    #    fade-in animation or shared material modified by another animator), default OriginalAlpha to 0.5f (1.0x opacity in
    #    Ori's 2x multiplier UberShaders) instead of 0.0f! This fixes all invisible Prologue cutscene illustrations (Image4-6),
    #    foreground/background fade layers, and OptionsScreen visibility!
    old_orig_alpha = (
        "IL_007d:\n"
        "\t{\n"
        "\t\tfloat L_22 = V_0;\n"
        "\t\t__this->___OriginalAlpha = L_22;\n"
        "\t\treturn;\n"
        "\t}"
    )
    new_orig_alpha = (
        "IL_007d:\n"
        "\t{\n"
        "\t\t__this->___OriginalAlpha = (0.5f);\n"
        "\t\treturn;\n"
        "\t}"
    )
    if "__this->___OriginalAlpha = (0.5f);" not in content:
        if old_orig_alpha not in content:
            raise RuntimeError("Could not find IL_007d in RendererData__ctor (Assembly-CSharp__25.cpp)")
        content = content.replace(old_orig_alpha, new_orig_alpha, 1)

    # 2. Export OriPort_UpdateTurbulenceGlobals() so OriPortManualPresenter_RenderFrame updates wind/turbulence shader globals
    #    every frame before manual Camera.Render() (since TurbulenceManager.OnRenderObject only fires for its own GameObject's camera).
    turb_helper = (
        "IL2CPP_EXTERN_C void OriPort_UpdateTurbulenceGlobals()\n"
        "{\n"
        "\tstatic bool s_init = false;\n"
        "\tif (!s_init)\n"
        "\t{\n"
        "\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&TurbulenceManager_t5F2ACC34B8AB3E82CD2028AC0A8737FDD118F450_il2cpp_TypeInfo_var);\n"
        "\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);\n"
        "\t\ts_init = true;\n"
        "\t}\n"
        "\tTurbulenceManager_t5F2ACC34B8AB3E82CD2028AC0A8737FDD118F450* mgr = ((TurbulenceManager_t5F2ACC34B8AB3E82CD2028AC0A8737FDD118F450_StaticFields*)il2cpp_codegen_static_fields_for(TurbulenceManager_t5F2ACC34B8AB3E82CD2028AC0A8737FDD118F450_il2cpp_TypeInfo_var))->___Instance;\n"
        "\til2cpp_codegen_runtime_class_init_inline(Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);\n"
        "\tif (mgr != NULL && Object_op_Implicit_m93896EF7D68FA113C42D3FE2BC6F661FC7EF514A(mgr, NULL))\n"
        "\t{\n"
        "\t\tTurbulenceManager_UpdateShaderGlobalsForManualRender_m3C9BB9E2270E651E1489042F1116930816C6CA81(mgr, NULL);\n"
        "\t}\n"
        "}\n"
    )
    turb_target = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void TurbulenceManager_OnRenderObject_mA6E707E9EEFAF81D67E7783C48370658C94B5A7D"
    if "void OriPort_UpdateTurbulenceGlobals()" not in content:
        if turb_target not in content:
            raise RuntimeError("Could not find TurbulenceManager_OnRenderObject in Assembly-CSharp__25.cpp")
        content = content.replace(turb_target, turb_helper + turb_target, 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__25.cpp (TransparencyAnimator+RendererData OriginalAlpha fix + TurbulenceManager manual render globals)")


def patch_assembly_csharp_26(cpp_dir: str) -> None:
    path = os.path.join(cpp_dir, "Assembly-CSharp__26.cpp")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Fix UberAlphaBuffer.SetCurrentAlphaGrab to use Shader.SetGlobalTexture("_AlphaGrabTex", m_alphaBuffer)
    #    instead of the stripped/deprecated RenderTexture.SetGlobalShaderProperty.
    extern_set_global_tex = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Shader_SetGlobalTexture_mAB95343764A1E9214DF3D80E029E03F6AD0BE230 (String_t* ___0_name, Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* ___1_value, const RuntimeMethod* method);\n"
    alpha_grab_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void UberAlphaBuffer_SetCurrentAlphaGrab_m69077B2FA1A7F07E8B64E8E4FD884979B6F50E6C"
    if extern_set_global_tex not in content:
        content = content.replace(alpha_grab_decl, extern_set_global_tex + alpha_grab_decl, 1)

    old_set_prop = "RenderTexture_SetGlobalShaderProperty_m7BBA88435EDF79EBB5275B3CF84EBEC897EEAAAA(L_2, _stringLiteral38EC5582E0AA27A2D5C239FE57D3F7595653A003, NULL);"
    new_set_prop = "Shader_SetGlobalTexture_mAB95343764A1E9214DF3D80E029E03F6AD0BE230(_stringLiteral38EC5582E0AA27A2D5C239FE57D3F7595653A003, L_2, NULL);"
    if old_set_prop in content:
        content = content.replace(old_set_prop, new_set_prop, 1)

    # 2. Route UberPostProcess.OnRenderImage to DoPost instead of DoCompatibilityPost on iOS so full color grading,
    #    nighttime curves, bloom, vignette, and UberAlphaBuffer are active!
    on_render_image_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void UberPostProcess_OnRenderImage_mD51A4F9A6598D5179C10BE516BE243B1EA51BA53"
    on_render_image_body = (
        "\t{\n"
        "\t\tUberPostProcess_DoPost_m6A2D0C46B4E566F7496AC41A7502DA9E36305DD1(__this, ___0_source, ___1_destination, NULL);\n"
        "\t\treturn;\n"
        "\t}"
    )
    content = replace_func_body(content, on_render_image_decl, on_render_image_body)

    # 3. In UberPostProcess.DoPost:
    #    - Initialize RenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27_il2cpp_TypeInfo_var metadata
    #    - Ensure __this->___PostTarget is allocated/resized to match ___0_source width/height (since OriPortManualPresenter
    #      passes m_frame with dynamic resolution scaling)
    #    - Null-check UberUIPostProcess.Instance before rendering its camera so scenes without UberUIPostProcess still execute
    #      Pass 3 (final tone-mapping/contrast/brightness blit from PostTarget to destination)!
    old_dopost_meta = "\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);\n\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&UberPostCacheIds_t9EBFAA44CA219ABF30A1382159A47EDE00B1FC26_il2cpp_TypeInfo_var);"
    new_dopost_meta = (
        "\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);\n"
        "\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&RenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27_il2cpp_TypeInfo_var);\n"
        "\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&UberPostCacheIds_t9EBFAA44CA219ABF30A1382159A47EDE00B1FC26_il2cpp_TypeInfo_var);"
    )
    if new_dopost_meta not in content:
        if old_dopost_meta not in content:
            raise RuntimeError("Could not find metadata init in UberPostProcess_DoPost (Assembly-CSharp__26.cpp)")
        content = content.replace(old_dopost_meta, new_dopost_meta, 1)

    old_il_003c = (
        "IL_003c:\n"
        "\t{\n"
        "\t\tV_0 = (RenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27*)NULL;"
    )
    new_il_003c = (
        "IL_003c:\n"
        "\t{\n"
        "\t\tRenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* pt = __this->___PostTarget;\n"
        "\t\til2cpp_codegen_runtime_class_init_inline(Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);\n"
        "\t\tint32_t srcW = VirtualFuncInvoker0< int32_t >::Invoke(4, ___0_source);\n"
        "\t\tint32_t srcH = VirtualFuncInvoker0< int32_t >::Invoke(6, ___0_source);\n"
        "\t\tif (!Object_op_Implicit_m93896EF7D68FA113C42D3FE2BC6F661FC7EF514A(pt, NULL) ||\n"
        "\t\t    VirtualFuncInvoker0< int32_t >::Invoke(4, pt) != srcW ||\n"
        "\t\t    VirtualFuncInvoker0< int32_t >::Invoke(6, pt) != srcH)\n"
        "\t\t{\n"
        "\t\t\tUberPostProcess_DestroyTargetTex_m860248A615B4855B59E8255CF1A1AEC1DF20E8D3(__this, pt, NULL);\n"
        "\t\t\tRenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* newPt = (RenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27*)il2cpp_codegen_object_new(RenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27_il2cpp_TypeInfo_var);\n"
        "\t\t\tRenderTexture__ctor_m53215A8EDDE262932758186108347685F6A512C4(newPt, srcW, srcH, ((int32_t)24), 0, NULL);\n"
        "\t\t\t__this->___PostTarget = newPt;\n"
        "\t\t\tIl2CppCodeGenWriteBarrier((void**)(&__this->___PostTarget), (void*)newPt);\n"
        "\t\t}\n"
        "\t\tV_0 = (RenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27*)NULL;"
    )
    if "RenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* pt = __this->___PostTarget;" not in content:
        if old_il_003c not in content:
            raise RuntimeError("Could not find IL_003c in UberPostProcess_DoPost (Assembly-CSharp__26.cpp)")
        content = content.replace(old_il_003c, new_il_003c, 1)

    old_ui_post = (
        "\t\tUberUIPostProcess_t57A61E7D95BF15C08A41B787A92895687CC9BE4C* L_75;\n"
        "\t\tL_75 = UberUIPostProcess_get_Instance_mE806F25F0167F575C457C0B0786E52898731FAAC_inline(NULL);\n"
        "\t\tNullCheck(L_75);\n"
        "\t\tCamera_tA92CC927D7439999BC82DBEDC0AA45B470F9E184* L_76 = L_75->___Camera;\n"
        "\t\tCamera_tA92CC927D7439999BC82DBEDC0AA45B470F9E184* L_77 = L_76;\n"
        "\t\tRenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* L_78 = __this->___PostTarget;\n"
        "\t\tNullCheck(L_77);\n"
        "\t\tCamera_set_targetTexture_mE6C740F21A72DA47FB5B1D31D208710738A836C4(L_77, L_78, NULL);\n"
        "\t\tCamera_tA92CC927D7439999BC82DBEDC0AA45B470F9E184* L_79 = L_77;\n"
        "\t\tNullCheck(L_79);\n"
        "\t\tRect_tA04E0F8A1830E767F40FB27ECD8D309303571F0D L_80;\n"
        "\t\tL_80 = Camera_get_rect_m848C23B32814D1351E43F0A0110DB8ECA19C6772(L_79, NULL);\n"
        "\t\tV_4 = L_80;\n"
        "\t\tCamera_tA92CC927D7439999BC82DBEDC0AA45B470F9E184* L_81 = L_79;\n"
        "\t\tRect_tA04E0F8A1830E767F40FB27ECD8D309303571F0D L_82;\n"
        "\t\tmemset((&L_82), 0, sizeof(L_82));\n"
        "\t\tRect__ctor_m18C3033D135097BEE424AAA68D91C706D2647F23_inline((&L_82), (0.0f), (0.0f), (1.0f), (1.0f), NULL);\n"
        "\t\tNullCheck(L_81);\n"
        "\t\tCamera_set_rect_mA81158BC169AF8674DE240AE9460FC5A0EADBB19(L_81, L_82, NULL);\n"
        "\t\tCamera_tA92CC927D7439999BC82DBEDC0AA45B470F9E184* L_83 = L_81;\n"
        "\t\tNullCheck(L_83);\n"
        "\t\tCamera_Render_m6089001EB6710DA9A21C87185D65922F13A24509(L_83, NULL);\n"
        "\t\tCamera_tA92CC927D7439999BC82DBEDC0AA45B470F9E184* L_84 = L_83;\n"
        "\t\tRect_tA04E0F8A1830E767F40FB27ECD8D309303571F0D L_85 = V_4;\n"
        "\t\tNullCheck(L_84);\n"
        "\t\tCamera_set_rect_mA81158BC169AF8674DE240AE9460FC5A0EADBB19(L_84, L_85, NULL);\n"
        "\t\tNullCheck(L_84);\n"
        "\t\tCamera_set_targetTexture_mE6C740F21A72DA47FB5B1D31D208710738A836C4(L_84, (RenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27*)NULL, NULL);"
    )
    new_ui_post = (
        "\t\tUberUIPostProcess_t57A61E7D95BF15C08A41B787A92895687CC9BE4C* L_75;\n"
        "\t\tL_75 = UberUIPostProcess_get_Instance_mE806F25F0167F575C457C0B0786E52898731FAAC_inline(NULL);\n"
        "\t\tif (L_75 != NULL && L_75->___Camera != NULL)\n"
        "\t\t{\n"
        "\t\t\tCamera_tA92CC927D7439999BC82DBEDC0AA45B470F9E184* L_77 = L_75->___Camera;\n"
        "\t\t\tRenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* L_78 = __this->___PostTarget;\n"
        "\t\t\tCamera_set_targetTexture_mE6C740F21A72DA47FB5B1D31D208710738A836C4(L_77, L_78, NULL);\n"
        "\t\t\tRect_tA04E0F8A1830E767F40FB27ECD8D309303571F0D L_80 = Camera_get_rect_m848C23B32814D1351E43F0A0110DB8ECA19C6772(L_77, NULL);\n"
        "\t\t\tV_4 = L_80;\n"
        "\t\t\tRect_tA04E0F8A1830E767F40FB27ECD8D309303571F0D L_82;\n"
        "\t\t\tmemset((&L_82), 0, sizeof(L_82));\n"
        "\t\t\tRect__ctor_m18C3033D135097BEE424AAA68D91C706D2647F23_inline((&L_82), (0.0f), (0.0f), (1.0f), (1.0f), NULL);\n"
        "\t\t\tCamera_set_rect_mA81158BC169AF8674DE240AE9460FC5A0EADBB19(L_77, L_82, NULL);\n"
        "\t\t\tCamera_Render_m6089001EB6710DA9A21C87185D65922F13A24509(L_77, NULL);\n"
        "\t\t\tCamera_set_rect_mA81158BC169AF8674DE240AE9460FC5A0EADBB19(L_77, V_4, NULL);\n"
        "\t\t\tCamera_set_targetTexture_mE6C740F21A72DA47FB5B1D31D208710738A836C4(L_77, (RenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27*)NULL, NULL);\n"
        "\t\t}"
    )
    if "if (L_75 != NULL && L_75->___Camera != NULL)" not in content:
        if old_ui_post not in content:
            raise RuntimeError("Could not find UberUIPostProcess block in UberPostProcess_DoPost (Assembly-CSharp__26.cpp)")
        content = content.replace(old_ui_post, new_ui_post, 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Patched Assembly-CSharp__26.cpp (UberPostProcess.DoPost enabled on iOS + UberAlphaBuffer Shader.SetGlobalTexture fix)")


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
    patch_assembly_csharp_3(cpp_dir)
    patch_assembly_csharp_10(cpp_dir)
    patch_assembly_csharp_11(cpp_dir)
    patch_assembly_csharp_13(cpp_dir)
    patch_assembly_csharp_17(cpp_dir)
    patch_assembly_csharp_21(cpp_dir)
    patch_assembly_csharp_23(cpp_dir)
    patch_assembly_csharp_25(cpp_dir)
    patch_assembly_csharp_26(cpp_dir)
    patch_assembly_csharp_27(cpp_dir)
    patch_assembly_csharp_29(cpp_dir)
    print("All iOS IL2CPP runtime patches applied successfully!")


if __name__ == "__main__":
    main()
