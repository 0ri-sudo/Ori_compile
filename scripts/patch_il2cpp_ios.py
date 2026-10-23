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
    snap_helper = """#include <stdio.h>
IL2CPP_EXTERN_C RuntimeClass* Cameras_t7935DA243CF368EB505A27E50005C968D54D5A90_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C RuntimeClass* Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void CameraPuppetController_Reset_m4707731712033B6CC8BE8954FF27AFACF81A5D8C (CameraPuppetController_tE58C8D776D2A6D6F92B40603A306EB81D2509F10* __this, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void GameplayCamera_GoToChaseMode_mFFC2F96AFB013160811FCF9DBACC7EB92561EB40 (GameplayCamera_t0939DE616725B1ED6EEBFB571FAFFE64C578EF00* __this, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void GameplayCamera_MoveCameraToTargetInstantly_m74A1E7974672F8B1DEFE7756070B1A7B3072F2B6 (GameplayCamera_t0939DE616725B1ED6EEBFB571FAFFE64C578EF00* __this, bool ___0_updateTargetPosition, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR Transform_tB27202C6F4E36D225EE28A13E4D662BF99785DB1* GameplayCamera_get_Target_mB590E93626C28F1E1C40BA4A66D970851B571A03 (GameplayCamera_t0939DE616725B1ED6EEBFB571FAFFE64C578EF00* __this, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR String_t* Object_get_name_mAC2F6B897CF1303BA4249B4CB55271AFACBB6392 (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C* __this, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool Object_op_Implicit_m93896EF7D68FA113C42D3FE2BC6F661FC7EF514A (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C* ___0_exists, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR Vector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 Transform_get_position_m69CD5FA214FDAE7BB701552943674846C220FDE1 (Transform_tB27202C6F4E36D225EE28A13E4D662BF99785DB1* __this, const RuntimeMethod* method);
IL2CPP_EXTERN_C void OriPort_StrToUtf8(String_t* s, char* out, int maxLen);

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

IL2CPP_EXTERN_C void OriPort_DumpCameraState(void* fpVoid)
{
\tFILE* fp = (FILE*)fpVoid;
\tif (fp == NULL) return;
\tstatic bool s_init = false;
\tif (!s_init)
\t{
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Cameras_t7935DA243CF368EB505A27E50005C968D54D5A90_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);
\t\ts_init = true;
\t}
\tfprintf(fp, "=== CAMERA STATE (UI.Cameras.Current) ===\\n");
\ttry
\t{
\t\til2cpp_codegen_runtime_class_init_inline(Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);
\t\tGameplayCamera_t0939DE616725B1ED6EEBFB571FAFFE64C578EF00* cam = ((Cameras_t7935DA243CF368EB505A27E50005C968D54D5A90_StaticFields*)il2cpp_codegen_static_fields_for(Cameras_t7935DA243CF368EB505A27E50005C968D54D5A90_il2cpp_TypeInfo_var))->___Current;
\t\tif (cam == NULL || !Object_op_Implicit_m93896EF7D68FA113C42D3FE2BC6F661FC7EF514A((Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)cam, NULL))
\t\t{
\t\t\tfprintf(fp, "GameplayCamera: NULL\\n\\n");
\t\t\treturn;
\t\t}
\t\tVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 camPos = (cam->___Transform != NULL && Object_op_Implicit_m93896EF7D68FA113C42D3FE2BC6F661FC7EF514A((Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)cam->___Transform, NULL)) ? Transform_get_position_m69CD5FA214FDAE7BB701552943674846C220FDE1(cam->___Transform, NULL) : cam->___CameraPositionForSampling;
\t\tVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 sampPos = cam->___CameraPositionForSampling;
\t\tfprintf(fp, "GameplayCamera.Position: (%.3f, %.3f, %.3f) | SamplingPos: (%.3f, %.3f, %.3f)\\n", camPos.___x, camPos.___y, camPos.___z, sampPos.___x, sampPos.___y, sampPos.___z);
\t\tTransform_tB27202C6F4E36D225EE28A13E4D662BF99785DB1* target = GameplayCamera_get_Target_mB590E93626C28F1E1C40BA4A66D970851B571A03(cam, NULL);
\t\tif (target != NULL && Object_op_Implicit_m93896EF7D68FA113C42D3FE2BC6F661FC7EF514A((Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)target, NULL))
\t\t{
\t\t\tchar tName[128];
\t\t\tOriPort_StrToUtf8(Object_get_name_mAC2F6B897CF1303BA4249B4CB55271AFACBB6392((Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)target, NULL), tName, sizeof(tName));
\t\t\tVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 tPos = Transform_get_position_m69CD5FA214FDAE7BB701552943674846C220FDE1(target, NULL);
\t\t\tfprintf(fp, "Target: '%s' at (%.3f, %.3f, %.3f)\\n", tName, tPos.___x, tPos.___y, tPos.___z);
\t\t}
\t\telse
\t\t{
\t\t\tfprintf(fp, "Target: NULL\\n");
\t\t}
\t\tCameraController_tDC4FF0FA10418272A26E5E7539156F4F4A98E8C5* ctrl = cam->___Controller;
\t\tif (ctrl != NULL && ctrl->___PuppetController != NULL)
\t\t{
\t\t\tCameraPuppetController_tE58C8D776D2A6D6F92B40603A306EB81D2509F10* pc = ctrl->___PuppetController;
\t\t\tTransform_tB27202C6F4E36D225EE28A13E4D662BF99785DB1* pup = pc->___CinematicPuppet;
\t\t\tif (pup != NULL && Object_op_Implicit_m93896EF7D68FA113C42D3FE2BC6F661FC7EF514A((Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)pup, NULL))
\t\t\t{
\t\t\t\tchar pName[128];
\t\t\t\tOriPort_StrToUtf8(Object_get_name_mAC2F6B897CF1303BA4249B4CB55271AFACBB6392((Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)pup, NULL), pName, sizeof(pName));
\t\t\t\tVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 pPos = Transform_get_position_m69CD5FA214FDAE7BB701552943674846C220FDE1(pup, NULL);
\t\t\t\tfprintf(fp, "PuppetController: Tween=%.3f CinematicPuppet='%s' at (%.3f, %.3f, %.3f)\\n\\n", pc->___Tween, pName, pPos.___x, pPos.___y, pPos.___z);
\t\t\t}
\t\t\telse
\t\t\t{
\t\t\t\tfprintf(fp, "PuppetController: Tween=%.3f CinematicPuppet=NULL\\n\\n", pc->___Tween);
\t\t\t}
\t\t}
\t\telse
\t\t{
\t\t\tfprintf(fp, "PuppetController: NULL\\n\\n");
\t\t}
\t}
\tcatch (Il2CppExceptionWrapper&)
\t{
\t\tfprintf(fp, "Exception while dumping camera state\\n\\n");
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
    dbg_cfg_decl_11 = (
        "struct OriPortDebugConfig { int32_t show_debug_btn; int32_t post_mode; int32_t motion_blur; int32_t bloom_blur; int32_t distortions; int32_t alpha_grab_mode; int32_t sanitizer_mode; float trans_alpha_default; int32_t turbulence_manual; int32_t fixed_hz; float time_scale; int32_t dump_now; int32_t panel_open; int32_t render_frame_exceptions; int32_t do_post_exceptions; int32_t dump_count; };\n"
        "IL2CPP_EXTERN_C OriPortDebugConfig g_OriDebug;\n"
    )
    if "IL2CPP_EXTERN_C OriPortDebugConfig g_OriDebug;" not in content:
        content = content.replace(inst_decl, dbg_cfg_decl_11 + inst_decl, 1)

    content = content.replace("if (L_7 <= 0.001f) { L_7 = 0.5f; }", "if (L_7 <= 0.001f) { L_7 = g_OriDebug.trans_alpha_default; }")
    old_legacy_mat_alpha = "\t\tfloat L_7 = L_6.___a;\n\t\t__this->___m_originalValue = L_7;"
    new_legacy_mat_alpha = "\t\tfloat L_7 = L_6.___a;\n\t\tif (L_7 <= 0.001f) { L_7 = g_OriDebug.trans_alpha_default; }\n\t\t__this->___m_originalValue = L_7;"
    if "if (L_7 <= 0.001f) { L_7 = g_OriDebug.trans_alpha_default; }" not in content:
        if old_legacy_mat_alpha not in content:
            raise RuntimeError("Could not find L_7 assignment in LegacyMaterialTransparencyAnimator_Start")
        content = content.replace(old_legacy_mat_alpha, new_legacy_mat_alpha, 1)

    content = content.replace("if (L_45 <= 0.001f) { L_45 = 0.5f; }", "if (L_45 <= 0.001f) { L_45 = g_OriDebug.trans_alpha_default; }")
    old_legacy_trans_alpha = "\t\tfloat L_45 = ((L_43)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_44)))->___a;\n\t\tNullCheck(L_41);\n\t\t(L_41)->SetAt(static_cast<il2cpp_array_size_t>(L_42), (float)L_45);"
    new_legacy_trans_alpha = "\t\tfloat L_45 = ((L_43)->GetAddressAt(static_cast<il2cpp_array_size_t>(L_44)))->___a;\n\t\tif (L_45 <= 0.001f) { L_45 = g_OriDebug.trans_alpha_default; }\n\t\tNullCheck(L_41);\n\t\t(L_41)->SetAt(static_cast<il2cpp_array_size_t>(L_42), (float)L_45);"
    if "if (L_45 <= 0.001f) { L_45 = g_OriDebug.trans_alpha_default; }" not in content:
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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
IL2CPP_EXTERN_C String_t* _stringLiteral1E5A05C3CB0E65E4EC72B4E86353C4177C469AEA;
IL2CPP_EXTERN_C String_t* _stringLiteral82CBFBC9D96154286C59A7A832F44ACA59CCC81D;
IL2CPP_EXTERN_C String_t* _stringLiteral12423BE7F4613F1339F6D1EB4246E858CEF4B093;
IL2CPP_EXTERN_C String_t* _stringLiteralD14C58C1EE361C9330F36F7B5E51A6947D158C6E;
IL2CPP_EXTERN_C String_t* _stringLiteral7078454B1E5C2E624B80831BA98D6DD13E9272FD;
IL2CPP_EXTERN_C String_t* _stringLiteralCE9C589CA1C6D1CB29B40C006FAA5870083004B1;
IL2CPP_EXTERN_C String_t* _stringLiteral38EC5582E0AA27A2D5C239FE57D3F7595653A003;
IL2CPP_EXTERN_C String_t* _stringLiteral47A3FAF17D89549FD0F0ECA7370B81F7C80DFCDE;
IL2CPP_EXTERN_C const RuntimeType* Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF_0_0_0_var;
IL2CPP_EXTERN_C RuntimeClass* Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C RuntimeClass* Type_t_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C RuntimeClass* Texture2D_tE6505BC111DD8A424A9DBE8E05D7D09E11FFFCF4_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C RuntimeClass* GUIStyle_t20BA2F9F3FE9D13AAA607EEEBE5547835A6F6580_il2cpp_TypeInfo_var;
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR MaterialU5BU5D_t2B1D11C42DB07A4400C0535F92DBB87A2E346D3D* Renderer_get_sharedMaterials_m0B61AFD8EDA35A70C796FFB2F28BB62380051ABF (Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF* __this, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool Renderer_get_enabled_mFDDF363859AEC88105A925FA7EA341C077B09B54 (Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF* __this, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Renderer_set_enabled_m015E6D7B825528A31182F267234CC6A925F71DA8 (Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF* __this, bool ___0_value, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int32_t Renderer_get_sortingOrder_m4CE7ADEEC8E2F28CC1D10B1D4091A10F8F1583FA (Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF* __this, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR GameObject_t76FEDD663AB33C991A9C9A23129337651094216F* Component_get_gameObject_m57AEFBB14DB39EC476F740BA000E170355DE691B (Component_t39FBE53E5EFCF4409111FB22C15FF73717632EC3* __this, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR Shader_tADC867D36B7876EE22427FAA2CE485105F4EE692* Material_get_shader_m8B0C11AE6F2AD7DE30AF52D3195EB716F7A71983 (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Material_set_shader_mBD3A0D9AB14DE2F7CD5F2775E9AD58E15424C171 (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, Shader_tADC867D36B7876EE22427FAA2CE485105F4EE692* ___0_value, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR int32_t Material_get_renderQueue_mC427C54D2667620CBB845559DA4DA31BE166C757 (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Material_set_renderQueue_mFBB72A781DCCF0D4B85670B597788EC2D02D1C14 (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, int32_t ___0_value, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool Material_HasProperty_mC09A83B44E368A217F606DD4954FA080CC03EC6C (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, String_t* ___0_name, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700* Material_GetTexture_mBA07A377A7DDD29CD53E6F687DE6D49A42C0C719 (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, String_t* ___0_name, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 Material_GetVector_mA2011D4DA2CC58003AE90DBF0802CF5EE31B014D (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, String_t* ___0_name, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Material_SetVector_m69444B8040D955821F241113446CC8713C9E12D1 (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, String_t* ___0_name, Vector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 ___1_value, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR Color_tD001788D726C3A7F1379BEED0260B9591F440C1F Material_GetColor_mAC702C70081A597DD2AA2F4627B1A1C65DDF6609 (Material_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* __this, String_t* ___0_name, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool String_StartsWith_mF75DBA1EB709811E711B44E26FF919C88A8E65C0 (String_t* __this, String_t* ___0_value, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR float Time_get_deltaTime_mC3195000401F0FD167DD2F948FD2BC58330D0865 (const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR float Time_get_timeScale_m1F45A413D4EEA08B1E0988022512C137F6C1E616 (const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Time_set_fixedDeltaTime_m8D8417B234CFF76AF81890D5AF67D8C54EFD189F (float ___0_value, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Time_set_timeScale_mEF84EE4B2376A458387648079B426B267862D331 (float ___0_value, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool Input_GetMouseButtonDown_m8DFC792D15FFF15D311614D5CC6C5D055E5A1DE3 (int32_t ___0_button, const RuntimeMethod* method);
IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool Input_GetKeyDown_mB237DEA6244132670D38990BAB77D813FBB028D2 (int32_t ___0_key, const RuntimeMethod* method);
IL2CPP_EXTERN_C void OriPort_UpdateTurbulenceGlobals();
IL2CPP_EXTERN_C void OriPort_DumpCameraState(void* fpVoid);
IL2CPP_EXTERN_C void OriPort_DumpPostProcessState(void* fpVoid);

struct OriPortDebugConfig {
\tint32_t post_mode; int32_t bloom_blur; int32_t motion_blur; int32_t distortions;
\tint32_t alpha_grab_mode; int32_t sanitize_mode; int32_t clamp_depth; float orig_alpha;
\tint32_t turbulence; int32_t fixed_hz; float time_scale; int32_t dump_now;
\tint32_t panel_open; int32_t exc_render_frame; int32_t exc_dopost; int32_t force_resanitize;
};

OriPortDebugConfig g_OriDebug = { 1, 1, 0, 1, 0, 1, 1, 0.5f, 1, 60, 1.0f, 0, 0, 0, 0, 0 };
float g_OriDefaultTransAlpha = 0.5f;
static int32_t s_showDebugBtn = 1;

IL2CPP_EXTERN_C void OriPort_StrToUtf8(String_t* str, char* buf, int maxLen)
{
\tif (buf == NULL || maxLen <= 0) return;
\tbuf[0] = '\\0';
\tif (str == NULL) return;
\tint32_t len = str->___m_stringLength;
\tif (len <= 0) return;
\tconst Il2CppChar* chars = &str->___m_firstChar;
\tint outIdx = 0;
\tfor (int32_t i = 0; i < len && outIdx < maxLen - 1; i++)
\t{
\t\tuint16_t c = (uint16_t)chars[i];
\t\tif (c < 0x80) buf[outIdx++] = (char)c;
\t\telse if (c < 0x800 && outIdx < maxLen - 2) { buf[outIdx++] = (char)(0xC0 | (c >> 6)); buf[outIdx++] = (char)(0x80 | (c & 0x3F)); }
\t\telse if (outIdx < maxLen - 3) { buf[outIdx++] = (char)(0xE0 | (c >> 12)); buf[outIdx++] = (char)(0x80 | ((c >> 6) & 0x3F)); buf[outIdx++] = (char)(0x80 | (c & 0x3F)); }
\t}
\tbuf[outIdx] = '\\0';
}

static char s_oriConfigPath[1024] = {0};
static char s_oriInspectorPath[1024] = {0};
static bool s_oriPathsInit = false;

static void OriPort_EnsurePaths()
{
\tif (s_oriPathsInit) return;
\ttry
\t{
\t\tString_t* pPath = Application_get_persistentDataPath_mC58BD3E1A20732E0A536491DBCAE6505B1624399(NULL);
\t\tif (pPath != NULL)
\t\t{
\t\t\tchar baseDir[896];
\t\t\tOriPort_StrToUtf8(pPath, baseDir, sizeof(baseDir));
\t\t\tif (baseDir[0] != '\\0')
\t\t\t{
\t\t\t\tsnprintf(s_oriConfigPath, sizeof(s_oriConfigPath), "%s/ori_debug.txt", baseDir);
\t\t\t\tsnprintf(s_oriInspectorPath, sizeof(s_oriInspectorPath), "%s/ori_inspector_log.txt", baseDir);
\t\t\t\ts_oriPathsInit = true;
\t\t\t}
\t\t}
\t}
\tcatch (Il2CppExceptionWrapper&) {}
}

static void OriPort_SaveConfig()
{
\tOriPort_EnsurePaths();
\tif (!s_oriPathsInit) return;
\tFILE* fp = fopen(s_oriConfigPath, "w");
\tif (!fp) return;
\tfprintf(fp, "# Ori iOS Live Debug Config (reloaded every 60 frames)\\n");
\tfprintf(fp, "show_debug_btn=%d\\n", (int)s_showDebugBtn);
\tfprintf(fp, "post_mode=%d\\n", (int)g_OriDebug.post_mode);
\tfprintf(fp, "motion_blur=%d\\n", (int)g_OriDebug.motion_blur);
\tfprintf(fp, "bloom_blur=%d\\n", (int)g_OriDebug.bloom_blur);
\tfprintf(fp, "distortions=%d\\n", (int)g_OriDebug.distortions);
\tfprintf(fp, "alpha_grab_mode=%d\\n", (int)g_OriDebug.alpha_grab_mode);
\tfprintf(fp, "sanitizer_mode=%d\\n", (int)g_OriDebug.sanitize_mode);
\tfprintf(fp, "trans_alpha_default=%.2f\\n", g_OriDefaultTransAlpha);
\tfprintf(fp, "turbulence_manual=%d\\n", (int)g_OriDebug.turbulence);
\tfprintf(fp, "fixed_hz=%d\\n", (int)g_OriDebug.fixed_hz);
\tfprintf(fp, "time_scale=%.2f\\n", g_OriDebug.time_scale);
\tfprintf(fp, "dump_now=%d\\n", (int)g_OriDebug.dump_now);
\tfclose(fp);
}

static void OriPort_ApplyTimeSettings()
{
\ttry
\t{
\t\tif (g_OriDebug.fixed_hz >= 30 && g_OriDebug.fixed_hz <= 240)
\t\t{
\t\t\tfloat targetFixed = 1.0f / (float)g_OriDebug.fixed_hz;
\t\t\tfloat curFixed = Time_get_fixedDeltaTime_m43136893D00AF5D5FE80AD05609558F6E2381381(NULL);
\t\t\tif (curFixed < targetFixed - 0.0001f || curFixed > targetFixed + 0.0001f)
\t\t\t\tTime_set_fixedDeltaTime_m8D8417B234CFF76AF81890D5AF67D8C54EFD189F(targetFixed, NULL);
\t\t}
\t\tif (g_OriDebug.time_scale >= 0.05f && g_OriDebug.time_scale <= 2.0f)
\t\t{
\t\t\tfloat curScale = Time_get_timeScale_m1F45A413D4EEA08B1E0988022512C137F6C1E616(NULL);
\t\t\tif (curScale > 0.001f && (curScale < g_OriDebug.time_scale - 0.01f || curScale > g_OriDebug.time_scale + 0.01f))
\t\t\t\tTime_set_timeScale_mEF84EE4B2376A458387648079B426B267862D331(g_OriDebug.time_scale, NULL);
\t\t}
\t}
\tcatch (Il2CppExceptionWrapper&) {}
}

static void OriPort_LoadOrSyncConfig()
{
\tOriPort_EnsurePaths();
\tif (!s_oriPathsInit) return;
\tFILE* fp = fopen(s_oriConfigPath, "r");
\tif (!fp) { OriPort_SaveConfig(); OriPort_ApplyTimeSettings(); return; }
\tchar line[256];
\tint32_t oldSan = g_OriDebug.sanitize_mode;
\twhile (fgets(line, sizeof(line), fp))
\t{
\t\tif (line[0] == '#' || line[0] == '\\n' || line[0] == '\\r') continue;
\t\tchar* eq = strchr(line, '=');
\t\tif (!eq) continue;
\t\t*eq = '\\0';
\t\tconst char* key = line;
\t\tconst char* val = eq + 1;
\t\tif (strcmp(key, "show_debug_btn") == 0) s_showDebugBtn = atoi(val);
\t\telse if (strcmp(key, "post_mode") == 0) g_OriDebug.post_mode = atoi(val);
\t\telse if (strcmp(key, "motion_blur") == 0) g_OriDebug.motion_blur = atoi(val);
\t\telse if (strcmp(key, "bloom_blur") == 0) g_OriDebug.bloom_blur = atoi(val);
\t\telse if (strcmp(key, "distortions") == 0) g_OriDebug.distortions = atoi(val);
\t\telse if (strcmp(key, "alpha_grab_mode") == 0) g_OriDebug.alpha_grab_mode = atoi(val);
\t\telse if (strcmp(key, "sanitizer_mode") == 0) g_OriDebug.sanitize_mode = atoi(val);
\t\telse if (strcmp(key, "trans_alpha_default") == 0) { g_OriDefaultTransAlpha = (float)atof(val); g_OriDebug.orig_alpha = g_OriDefaultTransAlpha; }
\t\telse if (strcmp(key, "turbulence_manual") == 0) g_OriDebug.turbulence = atoi(val);
\t\telse if (strcmp(key, "fixed_hz") == 0) g_OriDebug.fixed_hz = atoi(val);
\t\telse if (strcmp(key, "time_scale") == 0) g_OriDebug.time_scale = (float)atof(val);
\t\telse if (strcmp(key, "dump_now") == 0) g_OriDebug.dump_now = atoi(val);
\t}
\tfclose(fp);
\tif (g_OriDebug.sanitize_mode != oldSan) g_OriDebug.force_resanitize = 1;
\tOriPort_ApplyTimeSettings();
}

IL2CPP_EXTERN_C void OriPort_ApplyAlphaGrabOverride()
{
\tif (g_OriDebug.alpha_grab_mode != 2 && g_OriDebug.alpha_grab_mode != 3) return;
\tstatic bool s_texMetaInit = false;
\tif (!s_texMetaInit)
\t{
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Texture2D_tE6505BC111DD8A424A9DBE8E05D7D09E11FFFCF4_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral38EC5582E0AA27A2D5C239FE57D3F7595653A003);
\t\ts_texMetaInit = true;
\t}
\ttry
\t{
\t\tstatic Texture2D_tE6505BC111DD8A424A9DBE8E05D7D09E11FFFCF4* s_blackTex = NULL;
\t\tstatic Texture2D_tE6505BC111DD8A424A9DBE8E05D7D09E11FFFCF4* s_grayTex = NULL;
\t\til2cpp_codegen_runtime_class_init_inline(Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);
\t\tif (g_OriDebug.alpha_grab_mode == 2)
\t\t{
\t\t\tif (s_blackTex == NULL || Object_op_Equality_mB6120F782D83091EF56A198FCEBCF066DB4A9605(s_blackTex, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL))
\t\t\t{
\t\t\t\ts_blackTex = (Texture2D_tE6505BC111DD8A424A9DBE8E05D7D09E11FFFCF4*)il2cpp_codegen_object_new(Texture2D_tE6505BC111DD8A424A9DBE8E05D7D09E11FFFCF4_il2cpp_TypeInfo_var);
\t\t\t\tTexture2D__ctor_mECF60A9EC0638EC353C02C8E99B6B465D23BE917(s_blackTex, 1, 1, 4, (bool)0, NULL);
\t\t\t\tColor_tD001788D726C3A7F1379BEED0260B9591F440C1F c = { 0.0f, 0.0f, 0.0f, 0.0f };
\t\t\t\tTexture2D_SetPixel_m2CCFC5F729135D59DC4A697C2605A3FC5C8574DB(s_blackTex, 0, 0, c, NULL);
\t\t\t\tTexture2D_Apply_m36EE27E6F1BF7FB8C70A1D749DC4EE249810AA3A(s_blackTex, (bool)0, (bool)0, NULL);
\t\t\t}
\t\t\tShader_SetGlobalTexture_m9ECF95F30982225B918E7521B5F2C395CDC3DF16(_stringLiteral38EC5582E0AA27A2D5C239FE57D3F7595653A003, (Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700*)s_blackTex, NULL);
\t\t}
\t\telse if (g_OriDebug.alpha_grab_mode == 3)
\t\t{
\t\t\tif (s_grayTex == NULL || Object_op_Equality_mB6120F782D83091EF56A198FCEBCF066DB4A9605(s_grayTex, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL))
\t\t\t{
\t\t\t\ts_grayTex = (Texture2D_tE6505BC111DD8A424A9DBE8E05D7D09E11FFFCF4*)il2cpp_codegen_object_new(Texture2D_tE6505BC111DD8A424A9DBE8E05D7D09E11FFFCF4_il2cpp_TypeInfo_var);
\t\t\t\tTexture2D__ctor_mECF60A9EC0638EC353C02C8E99B6B465D23BE917(s_grayTex, 1, 1, 4, (bool)0, NULL);
\t\t\t\tColor_tD001788D726C3A7F1379BEED0260B9591F440C1F c = { 0.5f, 0.5f, 0.5f, 0.5f };
\t\t\t\tTexture2D_SetPixel_m2CCFC5F729135D59DC4A697C2605A3FC5C8574DB(s_grayTex, 0, 0, c, NULL);
\t\t\t\tTexture2D_Apply_m36EE27E6F1BF7FB8C70A1D749DC4EE249810AA3A(s_grayTex, (bool)0, (bool)0, NULL);
\t\t\t}
\t\t\tShader_SetGlobalTexture_m9ECF95F30982225B918E7521B5F2C395CDC3DF16(_stringLiteral38EC5582E0AA27A2D5C239FE57D3F7595653A003, (Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700*)s_grayTex, NULL);
\t\t}
\t}
\tcatch (Il2CppExceptionWrapper&) {}
}

static void OriPort_SanitizeSceneRenderers()
{
\tif (g_OriDebug.sanitize_mode == 0) return;
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
\t\tif (g_OriDebug.force_resanitize != 0)
\t\t{
\t\t\ts_lastSig = 0;
\t\t\tg_OriDebug.force_resanitize = 0;
\t\t}
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
\t\tif (g_OriDebug.sanitize_mode == 2)
\t\t{
\t\t\tfor (int32_t i = 0; i < count; i++)
\t\t\t{
\t\t\t\tObject_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C* obj = objs->GetAt(static_cast<il2cpp_array_size_t>(i));
\t\t\t\tif (obj == NULL) continue;
\t\t\t\tRenderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF* ren = (Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF*)CastclassClass((RuntimeObject*)obj, Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF_il2cpp_TypeInfo_var);
\t\t\t\tif (ren == NULL || Object_op_Equality_mB6120F782D83091EF56A198FCEBCF066DB4A9605(ren, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL)) continue;
\t\t\t\tRenderer_set_enabled_m015E6D7B825528A31182F267234CC6A925F71DA8(ren, (bool)1, NULL);
\t\t\t}
\t\t\treturn;
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

static void OriPort_DumpInspectorLog()
{
\tOriPort_EnsurePaths();
\tif (!s_oriPathsInit) return;
\tFILE* fp = fopen(s_oriInspectorPath, "w");
\tif (!fp) return;
\tfprintf(fp, "=== ORI IOS INSPECTOR LOG ===\\n");
\ttry
\t{
\t\tint32_t frame = Time_get_frameCount_m4A42E558A71301A216BDC49EC402D62F19C79667(NULL);
\t\tfloat dt = Time_get_deltaTime_mC3195000401F0FD167DD2F948FD2BC58330D0865(NULL);
\t\tfloat udt = Time_get_unscaledDeltaTime_mF057EECA857E5C0F90A3F910D26D3EE59F27C4B5(NULL);
\t\tfloat fdt = Time_get_fixedDeltaTime_m43136893D00AF5D5FE80AD05609558F6E2381381(NULL);
\t\tfloat ts = Time_get_timeScale_m1F45A413D4EEA08B1E0988022512C137F6C1E616(NULL);
\t\tfloat fps = (udt > 0.0001f) ? (1.0f / udt) : 0.0f;
\t\tScene_tA1DC762B79745EB5140F054C884855B922318356 sc = SceneManager_GetActiveScene_m0B320EC4302F51A71495D1CCD1A0FF9C2ED1FDC8(NULL);
\t\tString_t* scNameStr = Scene_get_name_m3C818DFA663E159274DAD823B780C7616C5E2A8C(&sc, NULL);
\t\tchar scName[128];
\t\tOriPort_StrToUtf8(scNameStr, scName, sizeof(scName));
\t\tfprintf(fp, "Frame: %d | FPS: %.1f | Scene: %s\\n", (int)frame, fps, scName);
\t\tfprintf(fp, "deltaTime: %.5f | fixedDeltaTime: %.5f | timeScale: %.2f\\n", dt, fdt, ts);
\t\tfprintf(fp, "Config: post_mode=%d motion_blur=%d bloom=%d distort=%d alpha_grab=%d sanitizer=%d trans_alpha=%.2f turb=%d fixed_hz=%d\\n",
\t\t\t(int)g_OriDebug.post_mode, (int)g_OriDebug.motion_blur, (int)g_OriDebug.bloom_blur,
\t\t\t(int)g_OriDebug.distortions, (int)g_OriDebug.alpha_grab_mode, (int)g_OriDebug.sanitize_mode,
\t\t\tg_OriDefaultTransAlpha, (int)g_OriDebug.turbulence, (int)g_OriDebug.fixed_hz);
\t\tfprintf(fp, "Exceptions Caught: RenderFrame=%d | DoPost=%d\\n\\n", (int)g_OriDebug.exc_render_frame, (int)g_OriDebug.exc_dopost);
\t}
\tcatch (Il2CppExceptionWrapper&) {}

\tOriPort_DumpCameraState((void*)fp);
\tfprintf(fp, "\\n");
\tOriPort_DumpPostProcessState((void*)fp);
\tfprintf(fp, "\\n=== SCENE RENDERERS ===\\n");

\ttry
\t{
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&_stringLiteral47A3FAF17D89549FD0F0ECA7370B81F7C80DFCDE);
\t\tRuntimeTypeHandle_t332A452B8B6179E4469B69525D0FE82A88030F7B rHandle = { reinterpret_cast<intptr_t>(Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF_0_0_0_var) };
\t\til2cpp_codegen_runtime_class_init_inline(Type_t_il2cpp_TypeInfo_var);
\t\tType_t* rType = Type_GetTypeFromHandle_m6062B81682F79A4D6DF2640692EE6D9987858C57(rHandle, NULL);
\t\til2cpp_codegen_runtime_class_init_inline(Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);
\t\tObjectU5BU5D_tD4BF1BEC72A31DF6611C0B8FA3112AF128FC3F8A* objs = Object_FindObjectsOfType_m3F1266E2DA67B067B22A3105C8F86A4EECCFEC4A(rType, NULL);
\t\tif (objs != NULL)
\t\t{
\t\t\tint32_t count = (int32_t)(((RuntimeArray*)objs)->max_length);
\t\t\tfprintf(fp, "Total Renderers: %d\\n", (int)count);
\t\t\tfor (int32_t i = 0; i < count; i++)
\t\t\t{
\t\t\t\tObject_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C* obj = objs->GetAt(static_cast<il2cpp_array_size_t>(i));
\t\t\t\tif (obj == NULL) continue;
\t\t\t\tRenderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF* ren = (Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF*)CastclassClass((RuntimeObject*)obj, Renderer_t320575F223BCB177A982E5DDB5DB19FAA89E7FBF_il2cpp_TypeInfo_var);
\t\t\t\tif (ren == NULL || Object_op_Equality_mB6120F782D83091EF56A198FCEBCF066DB4A9605(ren, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL)) continue;
\t\t\t\tbool en = Renderer_get_enabled_mFDDF363859AEC88105A925FA7EA341C077B09B54(ren, NULL);
\t\t\t\tint32_t sortOrder = Renderer_get_sortingOrder_m4CE7ADEEC8E2F28CC1D10B1D4091A10F8F1583FA(ren, NULL);
\t\t\t\tchar goName[128] = "<null>";
\t\t\t\tGameObject_t76FEDD663AB33C991A9C9A23129337651094216F* go = Component_get_gameObject_m57AEFBB14DB39EC476F740BA000E170355DE691B((Component_t39FBE53E5EFCF4409111FB22C15FF73717632EC3*)ren, NULL);
\t\t\t\tif (go != NULL && !Object_op_Equality_mB6120F782D83091EF56A198FCEBCF066DB4A9605((Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)go, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL))
\t\t\t\t{
\t\t\t\t\tOriPort_StrToUtf8(Object_get_name_mAC2F6B897CF1303BA4249B4CB55271AFACBB6392((Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)go, NULL), goName, sizeof(goName));
\t\t\t\t}
\t\t\t\tMaterialU5BU5D_t2B1D11C42DB07A4400C0535F92DBB87A2E346D3D* mats = Renderer_get_sharedMaterials_m0B61AFD8EDA35A70C796FFB2F28BB62380051ABF(ren, NULL);
\t\t\t\tif (mats == NULL) continue;
\t\t\t\tint32_t mCount = (int32_t)(((RuntimeArray*)mats)->max_length);
\t\t\t\tfor (int32_t j = 0; j < mCount; j++)
\t\t\t\t{
\t\t\t\t\tMaterial_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* mat = mats->GetAt(static_cast<il2cpp_array_size_t>(j));
\t\t\t\t\tif (mat == NULL || Object_op_Equality_mB6120F782D83091EF56A198FCEBCF066DB4A9605(mat, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL)) continue;
\t\t\t\t\tShader_tADC867D36B7876EE22427FAA2CE485105F4EE692* sh = Material_get_shader_m8B0C11AE6F2AD7DE30AF52D3195EB716F7A71983(mat, NULL);
\t\t\t\t\tchar shName[128] = "<null>";
\t\t\t\t\tif (sh != NULL && !Object_op_Equality_mB6120F782D83091EF56A198FCEBCF066DB4A9605(sh, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL))
\t\t\t\t\t{
\t\t\t\t\t\tOriPort_StrToUtf8(Object_get_name_mAC2F6B897CF1303BA4249B4CB55271AFACBB6392(sh, NULL), shName, sizeof(shName));
\t\t\t\t\t}
\t\t\t\t\tint32_t rq = Material_get_renderQueue_mC427C54D2667620CBB845559DA4DA31BE166C757(mat, NULL);
\t\t\t\t\tfloat dfx = -999.0f;
\t\t\t\t\tif (Material_HasProperty_mC09A83B44E368A217F606DD4954FA080CC03EC6C(mat, _stringLiteral57731D1C7614FDA9B9F849E36B9C6D9B7278712C, NULL))
\t\t\t\t\t{
\t\t\t\t\t\tVector4_t58B63D32F48C0DBF50DE2C60794C4676C80EDBE3 df = Material_GetVector_mA2011D4DA2CC58003AE90DBF0802CF5EE31B014D(mat, _stringLiteral57731D1C7614FDA9B9F849E36B9C6D9B7278712C, NULL);
\t\t\t\t\t\tdfx = df.___x;
\t\t\t\t\t}
\t\t\t\t\tColor_tD001788D726C3A7F1379BEED0260B9591F440C1F col = { -1.0f, -1.0f, -1.0f, -1.0f };
\t\t\t\t\tif (Material_HasProperty_mC09A83B44E368A217F606DD4954FA080CC03EC6C(mat, _stringLiteral47A3FAF17D89549FD0F0ECA7370B81F7C80DFCDE, NULL))
\t\t\t\t\t{
\t\t\t\t\t\tcol = Material_GetColor_mAC702C70081A597DD2AA2F4627B1A1C65DDF6609(mat, _stringLiteral47A3FAF17D89549FD0F0ECA7370B81F7C80DFCDE, NULL);
\t\t\t\t\t}
\t\t\t\t\tfprintf(fp, "[%d.%d] GO='%s' | en=%d | sort=%d | rq=%d | shader='%s' | df=%.2f | col=(%.2f,%.2f,%.2f,%.2f)\\n",
\t\t\t\t\t\t(int)i, (int)j, goName, (int)en, (int)sortOrder, (int)rq, shName, dfx, col.___r, col.___g, col.___b, col.___a);
\t\t\t\t}
\t\t\t}
\t\t}
\t}
\tcatch (Il2CppExceptionWrapper&)
\t{
\t\tfprintf(fp, "[Exception while enumerating renderers]\\n");
\t}
\tfclose(fp);
}

static void OriPort_DrawDebugOverlay()
{
\tif (!s_showDebugBtn && !g_OriDebug.panel_open) return;
\tstatic bool s_guiMetaInit = false;
\tif (!s_guiMetaInit)
\t{
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&GUI_tA9CDB3D69DB13D51AD83ABDB587EF95947EC2D2A_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Texture2D_tE6505BC111DD8A424A9DBE8E05D7D09E11FFFCF4_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&GUIStyle_t20BA2F9F3FE9D13AAA607EEEBE5547835A6F6580_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);
\t\ts_guiMetaInit = true;
\t}
\ttry
\t{
\t\tstatic Texture2D_tE6505BC111DD8A424A9DBE8E05D7D09E11FFFCF4* s_whiteTex = NULL;
\t\tstatic GUIStyle_t20BA2F9F3FE9D13AAA607EEEBE5547835A6F6580* s_lblStyle = NULL;
\t\til2cpp_codegen_runtime_class_init_inline(Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);
\t\tif (s_whiteTex == NULL || Object_op_Equality_mB6120F782D83091EF56A198FCEBCF066DB4A9605(s_whiteTex, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL))
\t\t{
\t\t\ts_whiteTex = (Texture2D_tE6505BC111DD8A424A9DBE8E05D7D09E11FFFCF4*)il2cpp_codegen_object_new(Texture2D_tE6505BC111DD8A424A9DBE8E05D7D09E11FFFCF4_il2cpp_TypeInfo_var);
\t\t\tTexture2D__ctor_mECF60A9EC0638EC353C02C8E99B6B465D23BE917(s_whiteTex, 1, 1, 4, (bool)0, NULL);
\t\t\tColor_tD001788D726C3A7F1379BEED0260B9591F440C1F w = { 1.0f, 1.0f, 1.0f, 1.0f };
\t\t\tTexture2D_SetPixel_m2CCFC5F729135D59DC4A697C2605A3FC5C8574DB(s_whiteTex, 0, 0, w, NULL);
\t\t\tTexture2D_Apply_m36EE27E6F1BF7FB8C70A1D749DC4EE249810AA3A(s_whiteTex, (bool)0, (bool)0, NULL);
\t\t}
\t\til2cpp_codegen_runtime_class_init_inline(GUI_tA9CDB3D69DB13D51AD83ABDB587EF95947EC2D2A_il2cpp_TypeInfo_var);
\t\tif (s_lblStyle == NULL)
\t\t{
\t\t\tGUISkin_t8C65CE1424D4B5D8D73022E266BDAD3BDE8612D9* skin = GUI_get_skin_m97EC9EB4628B311C0DB7DF9FB19FAD82D6790A1B(NULL);
\t\t\tif (skin != NULL)
\t\t\t{
\t\t\t\tGUIStyle_t20BA2F9F3FE9D13AAA607EEEBE5547835A6F6580* baseLbl = GUISkin_get_label_m99E1A8D6D8592F88F581437D24DB1EDE05C63E5E(skin, NULL);
\t\t\t\tif (baseLbl != NULL)
\t\t\t\t{
\t\t\t\t\ts_lblStyle = (GUIStyle_t20BA2F9F3FE9D13AAA607EEEBE5547835A6F6580*)il2cpp_codegen_object_new(GUIStyle_t20BA2F9F3FE9D13AAA607EEEBE5547835A6F6580_il2cpp_TypeInfo_var);
\t\t\t\t\tGUIStyle__ctor_m17492C8BACB0D28C7701C11500A7132F11B5F04E(s_lblStyle, baseLbl, NULL);
\t\t\t\t\tGUIStyle_set_alignment_mEDC62A775C9551DBD1FEE4043F115E034EF12937(s_lblStyle, 4, NULL);
\t\t\t\t\tGUIStyle_set_fontStyle_m4166D61FBF25225F4A85BBEABCECE3F2DCEE714D(s_lblStyle, 1, NULL);
\t\t\t\t\tGUIStyleState_t7A948723D9DCDFD8EE4F418B6EC909C18E023F95* st = GUIStyle_get_normal_mDEA2808FBD692E505784BD9E521738B4321BCA8F(s_lblStyle, NULL);
\t\t\t\t\tif (st != NULL)
\t\t\t\t\t{
\t\t\t\t\t\tColor_tD001788D726C3A7F1379BEED0260B9591F440C1F w = { 1.0f, 1.0f, 1.0f, 1.0f };
\t\t\t\t\t\tGUIStyleState_set_textColor_m5868D12858E6402247953BCCDDA7A543BE6084F1(st, w, NULL);
\t\t\t\t\t}
\t\t\t\t}
\t\t\t}
\t\t}
\t\tif (s_lblStyle == NULL) return;

\t\tint32_t sw = Screen_get_width_mF608FF3252213E7EFA1F0D2F744C28110E9E5AC9(NULL);
\t\tint32_t sh = Screen_get_height_m01A3102DE71EE1FBEA51D09D6B0261CF864FE8F9(NULL);
\t\tfloat scale = (float)sh / 720.0f;
\t\tif (scale < 0.75f) scale = 0.75f;
\t\tGUIStyle_set_fontSize_m7F6DFD61AC55072C95DC3825B77FAE3F75F1CCFF(s_lblStyle, (int32_t)(16.0f * scale), NULL);

\t\tstatic int32_t s_lastTapFrame = -10;
\t\tint32_t curFrame = Time_get_frameCount_m4A42E558A71301A216BDC49EC402D62F19C79667(NULL);
\t\tbool tapped = false;
\t\tfloat tapX = -1.0f, tapY = -1.0f;
\t\tif (curFrame != s_lastTapFrame)
\t\t{
\t\t\tint32_t tc = Input_get_touchCount_m057388BFC67A0F4CA53764B1022867ED81D01E39(NULL);
\t\t\tfor (int32_t ti = 0; ti < tc; ti++)
\t\t\t{
\t\t\t\tTouch_t03E51455ED508492B3F278903A0114FA0E87B417 t = Input_GetTouch_m75D99FE801A94279874FA8DC6B6ADAD35F5123B1(ti, NULL);
\t\t\t\tif (Touch_get_phase_mB82409FB2BE1C32ABDBA6A72E52A099D28AB70B0(&t, NULL) == 0)
\t\t\t\t{
\t\t\t\t\tVector2_t1FD6F485C871E832B347AB2DC8CBA08B739D8DF7 p = Touch_get_position_m41B9EB0F3F3E1BE98CEB388253A9E31979CB964A(&t, NULL);
\t\t\t\t\ttapX = p.___x;
\t\t\t\t\ttapY = (float)sh - p.___y;
\t\t\t\t\ttapped = true;
\t\t\t\t\ts_lastTapFrame = curFrame;
\t\t\t\t\tbreak;
\t\t\t\t}
\t\t\t}
\t\t\tif (!tapped && Input_GetMouseButtonDown_m8DFC792D15FFF15D311614D5CC6C5D055E5A1DE3(0, NULL))
\t\t\t{
\t\t\t\tVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 mp = Input_get_mousePosition_mFF21FBD2647DAE2A23BD4C45571CA95D05A0A42C(NULL);
\t\t\t\ttapX = mp.___x;
\t\t\t\ttapY = (float)sh - mp.___y;
\t\t\t\ttapped = true;
\t\t\t\ts_lastTapFrame = curFrame;
\t\t\t}
\t\t\tif (Input_GetKeyDown_mB237DEA6244132670D38990BAB77D813FBB028D2(356, NULL) || Input_GetKeyDown_mB237DEA6244132670D38990BAB77D813FBB028D2(358, NULL))
\t\t\t{
\t\t\t\tg_OriDebug.panel_open = !g_OriDebug.panel_open;
\t\t\t\ts_lastTapFrame = curFrame;
\t\t\t}
\t\t}

\t\tColor_tD001788D726C3A7F1379BEED0260B9591F440C1F oldCol = GUI_get_color_m15488B4AD785D10DEB5C66398D0FA9A0C0EA7ABB(NULL);
\t\tMatrix4x4_tDB70CF134A14BA38190C59AA700BCE10E2AED3E6 oldMat = GUI_get_matrix_m3CA02DED0598EE32BD9E66CA533A78EFB0A246FC(NULL);
\t\tGUI_set_matrix_m7759FEC96FBCB97E02B1BA44D2EC1B3FEEFA257F(Matrix4x4_get_identity_m6568A73831F3E2D587420D20FF423959D7D8AB56_inline(NULL), NULL);

\t\tfloat bx = 24.0f * scale, by = 16.0f * scale, bw = 82.0f * scale, bh = 36.0f * scale;
\t\tRect_tA04E0F8A1830E767F40FB27ECD8D309303571F0D dbgRect = { bx, by, bw, bh };
\t\tif (tapped && tapX >= bx && tapX <= bx + bw && tapY >= by && tapY <= by + bh)
\t\t{
\t\t\tg_OriDebug.panel_open = !g_OriDebug.panel_open;
\t\t\ttapped = false;
\t\t}
\t\tColor_tD001788D726C3A7F1379BEED0260B9591F440C1F btnBg = { 0.1f, 0.15f, 0.25f, 0.85f };
\t\tGUI_set_color_mA44927D3F2ACB1E228815F10042A6F62B7645648(btnBg, NULL);
\t\tGUI_DrawTexture_m05F173ECE6F2D78FFBDEB0052EB58AC2B5A7420E(dbgRect, (Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700*)s_whiteTex, 0, (bool)1, NULL);
\t\tGUI_set_color_mA44927D3F2ACB1E228815F10042A6F62B7645648(Color_get_white_m068F5AF879B0FCA584E3693F762EA41BB65532C6_inline(NULL), NULL);
\t\tGUI_Label_m0D7BA53414421D71010DFF628EAA6CCCB3DE737E(dbgRect, il2cpp_codegen_string_new_wrapper(g_OriDebug.panel_open ? "[CLOSE]" : "[DBG]"), s_lblStyle, NULL);

\t\tif (g_OriDebug.panel_open)
\t\t{
\t\t\tfloat px = 24.0f * scale, py = 58.0f * scale, pw = 520.0f * scale, ph = 310.0f * scale;
\t\t\tRect_tA04E0F8A1830E767F40FB27ECD8D309303571F0D panRect = { px, py, pw, ph };
\t\t\tColor_tD001788D726C3A7F1379BEED0260B9591F440C1F panBg = { 0.05f, 0.07f, 0.12f, 0.90f };
\t\t\tGUI_set_color_mA44927D3F2ACB1E228815F10042A6F62B7645648(panBg, NULL);
\t\t\tGUI_DrawTexture_m05F173ECE6F2D78FFBDEB0052EB58AC2B5A7420E(panRect, (Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700*)s_whiteTex, 0, (bool)1, NULL);

\t\t\tfloat udt = Time_get_unscaledDeltaTime_mF057EECA857E5C0F90A3F910D26D3EE59F27C4B5(NULL);
\t\t\tfloat fps = (udt > 0.0001f) ? (1.0f / udt) : 0.0f;
\t\t\tchar hdr[160];
\t\t\tsnprintf(hdr, sizeof(hdr), "FPS: %.1f | Exc(RF:%d DP:%d) | ori_debug.txt Live", fps, (int)g_OriDebug.exc_render_frame, (int)g_OriDebug.exc_dopost);
\t\t\tRect_tA04E0F8A1830E767F40FB27ECD8D309303571F0D hdrRect = { px + 8.0f * scale, py + 4.0f * scale, pw - 16.0f * scale, 28.0f * scale };
\t\t\tGUI_set_color_mA44927D3F2ACB1E228815F10042A6F62B7645648(Color_get_white_m068F5AF879B0FCA584E3693F762EA41BB65532C6_inline(NULL), NULL);
\t\t\tGUI_Label_m0D7BA53414421D71010DFF628EAA6CCCB3DE737E(hdrRect, il2cpp_codegen_string_new_wrapper(hdr), s_lblStyle, NULL);

\t\t\tconst char* postNames[3] = { "Compat", "DoPost", "Blit" };
\t\t\tconst char* agNames[4] = { "UberAB", "ManGrab", "Black0", "Gray.5" };
\t\t\tconst char* sanNames[3] = { "OFF", "Normal", "ReEnAll" };
\t\t\tchar bLabels[10][64];
\t\t\tsnprintf(bLabels[0], 64, "Post: %s (%d)", postNames[g_OriDebug.post_mode % 3], (int)g_OriDebug.post_mode);
\t\t\tsnprintf(bLabels[1], 64, "MotionBlur: %s", g_OriDebug.motion_blur ? "ON" : "OFF");
\t\t\tsnprintf(bLabels[2], 64, "BloomBlur: %s", g_OriDebug.bloom_blur ? "ON" : "OFF");
\t\t\tsnprintf(bLabels[3], 64, "Distort: %s", g_OriDebug.distortions ? "ON" : "OFF");
\t\t\tsnprintf(bLabels[4], 64, "AlphaGrab: %s", agNames[g_OriDebug.alpha_grab_mode % 4]);
\t\t\tsnprintf(bLabels[5], 64, "Sanitizer: %s", sanNames[g_OriDebug.sanitize_mode % 3]);
\t\t\tsnprintf(bLabels[6], 64, "TransAlpha: %.1f", g_OriDefaultTransAlpha);
\t\t\tsnprintf(bLabels[7], 64, "Turbulence: %s", g_OriDebug.turbulence ? "ON" : "OFF");
\t\t\tsnprintf(bLabels[8], 64, "FixedHz:%d TS:%.2f", (int)g_OriDebug.fixed_hz, g_OriDebug.time_scale);
\t\t\tsnprintf(bLabels[9], 64, "[DUMP INSPECTOR LOG]");

\t\t\tfloat cw = (pw - 24.0f * scale) * 0.5f;
\t\t\tfloat ch = 46.0f * scale;
\t\t\tbool changed = false;
\t\t\tfor (int idx = 0; idx < 10; idx++)
\t\t\t{
\t\t\t\tint col = idx % 2;
\t\t\t\tint row = idx / 2;
\t\t\t\tfloat rx = px + 8.0f * scale + col * (cw + 8.0f * scale);
\t\t\t\tfloat ry = py + 36.0f * scale + row * (ch + 6.0f * scale);
\t\t\t\tRect_tA04E0F8A1830E767F40FB27ECD8D309303571F0D r = { rx, ry, cw, ch };
\t\t\t\tif (tapped && tapX >= rx && tapX <= rx + cw && tapY >= ry && tapY <= ry + ch)
\t\t\t\t{
\t\t\t\t\ttapped = false;
\t\t\t\t\tchanged = true;
\t\t\t\t\tif (idx == 0) g_OriDebug.post_mode = (g_OriDebug.post_mode + 1) % 3;
\t\t\t\t\telse if (idx == 1) g_OriDebug.motion_blur = !g_OriDebug.motion_blur;
\t\t\t\t\telse if (idx == 2) g_OriDebug.bloom_blur = !g_OriDebug.bloom_blur;
\t\t\t\t\telse if (idx == 3) g_OriDebug.distortions = !g_OriDebug.distortions;
\t\t\t\t\telse if (idx == 4) g_OriDebug.alpha_grab_mode = (g_OriDebug.alpha_grab_mode + 1) % 4;
\t\t\t\t\telse if (idx == 5) { g_OriDebug.sanitize_mode = (g_OriDebug.sanitize_mode + 1) % 3; g_OriDebug.force_resanitize = 1; }
\t\t\t\t\telse if (idx == 6) { g_OriDefaultTransAlpha = (g_OriDefaultTransAlpha < 0.25f) ? 0.5f : ((g_OriDefaultTransAlpha < 0.75f) ? 1.0f : 0.0f); g_OriDebug.orig_alpha = g_OriDefaultTransAlpha; }
\t\t\t\t\telse if (idx == 7) g_OriDebug.turbulence = !g_OriDebug.turbulence;
\t\t\t\t\telse if (idx == 8)
\t\t\t\t\t{
\t\t\t\t\t\tif (g_OriDebug.fixed_hz == 60 && g_OriDebug.time_scale > 0.9f) g_OriDebug.fixed_hz = 120;
\t\t\t\t\t\telse if (g_OriDebug.fixed_hz == 120 && g_OriDebug.time_scale > 0.9f) { g_OriDebug.fixed_hz = 60; g_OriDebug.time_scale = 0.5f; }
\t\t\t\t\t\telse if (g_OriDebug.time_scale > 0.4f) g_OriDebug.time_scale = 0.25f;
\t\t\t\t\t\telse g_OriDebug.time_scale = 1.0f;
\t\t\t\t\t\tOriPort_ApplyTimeSettings();
\t\t\t\t\t}
\t\t\t\t\telse if (idx == 9) g_OriDebug.dump_now = 1;
\t\t\t\t}
\t\t\t\tColor_tD001788D726C3A7F1379BEED0260B9591F440C1F cellBg = (idx == 9)
\t\t\t\t\t? Color_tD001788D726C3A7F1379BEED0260B9591F440C1F{ 0.15f, 0.45f, 0.20f, 0.92f }
\t\t\t\t\t: Color_tD001788D726C3A7F1379BEED0260B9591F440C1F{ 0.18f, 0.24f, 0.36f, 0.92f };
\t\t\t\tGUI_set_color_mA44927D3F2ACB1E228815F10042A6F62B7645648(cellBg, NULL);
\t\t\t\tGUI_DrawTexture_m05F173ECE6F2D78FFBDEB0052EB58AC2B5A7420E(r, (Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700*)s_whiteTex, 0, (bool)1, NULL);
\t\t\t\tGUI_set_color_mA44927D3F2ACB1E228815F10042A6F62B7645648(Color_get_white_m068F5AF879B0FCA584E3693F762EA41BB65532C6_inline(NULL), NULL);
\t\t\t\tGUI_Label_m0D7BA53414421D71010DFF628EAA6CCCB3DE737E(r, il2cpp_codegen_string_new_wrapper(bLabels[idx]), s_lblStyle, NULL);
\t\t\t}
\t\t\tif (changed) OriPort_SaveConfig();
\t\t}

\t\tGUI_set_color_mA44927D3F2ACB1E228815F10042A6F62B7645648(oldCol, NULL);
\t\tGUI_set_matrix_m7759FEC96FBCB97E02B1BA44D2EC1B3FEEFA257F(oldMat, NULL);
\t}
\tcatch (Il2CppExceptionWrapper&) {}
}
"""
    content = content.replace(render_frame_decl, extern_decls + render_frame_decl, 1)

    # 1. In OriPortManualPresenter_RenderFrame:
    #    - Sync ori_debug.txt every 60 frames & trigger OriPort_DumpInspectorLog() if dump_now != 0
    #    - Periodically run OriPort_SanitizeSceneRenderers() (every 15 frames)
    #    - Call OriPort_UpdateTurbulenceGlobals()
    #    - Call OriPortManualPresenter_UpdateAlphaGrab when alpha_grab_mode == 1
    old_render_call = """\t\t\t\tShader_SetGlobalFloat_m8AA7A4D7D73914A00D9207D78621EDDF70602FB0(_stringLiteral682BF2EFA52E75C110EBBFF64FA09D54B09DA240, (-1.0f), NULL);
\t\t\t\tOriPortManualPresenter_set_IsRenderingPresentedFrame_m1760BA79F65488022AE1A93714CC89A44E71424E_inline((bool)1, NULL);
\t\t\t\tCamera_tA92CC927D7439999BC82DBEDC0AA45B470F9E184* L_71 = V_1;
\t\t\t\tNullCheck(L_71);
\t\t\t\tCamera_Render_m6089001EB6710DA9A21C87185D65922F13A24509(L_71, NULL);
\t\t\t\tgoto IL_01b7;"""

    prev_render_call_1 = """\t\t\t\tstatic int32_t s_sanitizeCounter = 0;
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

    prev_render_call_2 = (
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

    new_render_call = (
        "\t\t\t\tstatic int32_t s_sanitizeCounter = 0;\n"
        "\t\t\t\tif ((s_sanitizeCounter % 60) == 0)\n"
        "\t\t\t\t{\n"
        "\t\t\t\t\tOriPort_LoadOrSyncConfig();\n"
        "\t\t\t\t}\n"
        "\t\t\t\tif (g_OriDebug.dump_now != 0)\n"
        "\t\t\t\t{\n"
        "\t\t\t\t\tg_OriDebug.dump_now = 0;\n"
        "\t\t\t\t\tOriPort_SaveConfig();\n"
        "\t\t\t\t\tOriPort_DumpInspectorLog();\n"
        "\t\t\t\t}\n"
        "\t\t\t\tif ((s_sanitizeCounter++ % 15) == 0 || g_OriDebug.force_resanitize != 0)\n"
        "\t\t\t\t{\n"
        "\t\t\t\t\tOriPort_SanitizeSceneRenderers();\n"
        "\t\t\t\t}\n"
        "\t\t\t\tOriPort_UpdateTurbulenceGlobals();\n"
        "\t\t\t\tShader_SetGlobalFloat_m8AA7A4D7D73914A00D9207D78621EDDF70602FB0(_stringLiteral682BF2EFA52E75C110EBBFF64FA09D54B09DA240, (-1.0f), NULL);\n"
        "\t\t\t\tOriPortManualPresenter_set_IsRenderingPresentedFrame_m1760BA79F65488022AE1A93714CC89A44E71424E_inline((bool)1, NULL);\n"
        "\t\t\t\tCamera_tA92CC927D7439999BC82DBEDC0AA45B470F9E184* L_71 = V_1;\n"
        "\t\t\t\tNullCheck(L_71);\n"
        "\t\t\t\tCamera_Render_m6089001EB6710DA9A21C87185D65922F13A24509(L_71, NULL);\n"
        "\t\t\t\tif (g_OriDebug.alpha_grab_mode == 1)\n"
        "\t\t\t\t{\n"
        "\t\t\t\t\ttry { OriPortManualPresenter_UpdateAlphaGrab_m6D5C8A797031A3CAABF1F73E449DA1A147570CEF(__this, V_2, V_3, NULL); }\n"
        "\t\t\t\t\tcatch (Il2CppExceptionWrapper&) {}\n"
        "\t\t\t\t}\n"
        "\t\t\t\tgoto IL_01b7;"
    )
    if prev_render_call_2 in content:
        content = content.replace(prev_render_call_2, new_render_call, 1)
    elif prev_render_call_1 in content:
        content = content.replace(prev_render_call_1, new_render_call, 1)
    elif "OriPort_LoadOrSyncConfig();" not in content.split(render_frame_decl, 1)[1]:
        if old_render_call not in content:
            raise RuntimeError("Could not find Camera_Render block in OriPortManualPresenter_RenderFrame")
        content = content.replace(old_render_call, new_render_call, 1)

    # 2. Wrap OriPortManualPresenter_RenderFrame call inside U3CStartU3Ed__13_MoveNext in a try/catch
    #    and count exceptions in g_OriDebug.exc_render_frame
    old_movenext_call = """IL_003d:
\t{
\t\t__this->___U3CU3E1__state = (-1);
\t\tOriPortManualPresenter_t2F5F855B4DF012477351066DD463FB5872874118* L_7 = V_1;
\t\tNullCheck(L_7);
\t\tOriPortManualPresenter_RenderFrame_m9CADB5C9F1B1990254DE31AA31AAB8DA5F9F8052(L_7, NULL);
\t\tgoto IL_0029;
\t}"""

    prev_movenext_call = """IL_003d:
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
\t\t\t\tg_OriDebug.exc_render_frame++;
\t\t\t}
\t\t}
\t\tgoto IL_0029;
\t}"""

    if prev_movenext_call in content:
        content = content.replace(prev_movenext_call, new_movenext_call, 1)
    elif "g_OriDebug.exc_render_frame++;" not in content:
        if old_movenext_call not in content:
            raise RuntimeError("Could not find IL_003d block in U3CStartU3Ed__13_MoveNext")
        content = content.replace(old_movenext_call, new_movenext_call, 1)

    # 3. Fix GUI.depth in OriPortManualPresenter_OnGUI and draw the in-game debug overlay
    on_gui_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void OriPortManualPresenter_OnGUI_m797B8337761723FC6A2D02EDAF956B10ED279B12"
    on_gui_body = """\tstatic bool s_Il2CppMethodInitialized;
\tif (!s_Il2CppMethodInitialized)
\t{
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&GUI_tA9CDB3D69DB13D51AD83ABDB587EF95947EC2D2A_il2cpp_TypeInfo_var);
\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);
\t\ts_Il2CppMethodInitialized = true;
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
\t\tRenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* L_0 = __this->___m_frame;
\t\til2cpp_codegen_runtime_class_init_inline(Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);
\t\tbool L_1 = Object_op_Equality_mB6120F782D83091EF56A198FCEBCF066DB4A9605(L_0, (Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)NULL, NULL);
\t\tif (!L_1)
\t\t{
\t\t\til2cpp_codegen_runtime_class_init_inline(GUI_tA9CDB3D69DB13D51AD83ABDB587EF95947EC2D2A_il2cpp_TypeInfo_var);
\t\t\tGUI_set_depth_m37E8C151AD6D1B28DDFABB64A0974398AA8EC44E(((int32_t)1000), NULL);
\t\t\tMatrix4x4_tDB70CF134A14BA38190C59AA700BCE10E2AED3E6 L_4 = GUI_get_matrix_m3CA02DED0598EE32BD9E66CA533A78EFB0A246FC(NULL);
\t\t\tColor_tD001788D726C3A7F1379BEED0260B9591F440C1F L_5 = GUI_get_color_m15488B4AD785D10DEB5C66398D0FA9A0C0EA7ABB(NULL);
\t\t\tMatrix4x4_tDB70CF134A14BA38190C59AA700BCE10E2AED3E6 L_6 = Matrix4x4_get_identity_m6568A73831F3E2D587420D20FF423959D7D8AB56_inline(NULL);
\t\t\tGUI_set_matrix_m7759FEC96FBCB97E02B1BA44D2EC1B3FEEFA257F(L_6, NULL);
\t\t\tColor_tD001788D726C3A7F1379BEED0260B9591F440C1F L_7 = Color_get_white_m068F5AF879B0FCA584E3693F762EA41BB65532C6_inline(NULL);
\t\t\tGUI_set_color_mA44927D3F2ACB1E228815F10042A6F62B7645648(L_7, NULL);
\t\t\tRect_tA04E0F8A1830E767F40FB27ECD8D309303571F0D L_8 = __this->___m_displayRect;
\t\t\tRenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* L_9 = __this->___m_frame;
\t\t\tGUI_DrawTexture_m05F173ECE6F2D78FFBDEB0052EB58AC2B5A7420E(L_8, L_9, 0, (bool)0, NULL);
\t\t\tGUI_set_color_mA44927D3F2ACB1E228815F10042A6F62B7645648(L_5, NULL);
\t\t\tGUI_set_matrix_m7759FEC96FBCB97E02B1BA44D2EC1B3FEEFA257F(L_4, NULL);
\t\t}
\t\tOriPort_DrawDebugOverlay();
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
    prev_orig_alpha = (
        "IL_007d:\n"
        "\t{\n"
        "\t\t__this->___OriginalAlpha = (0.5f);\n"
        "\t\treturn;\n"
        "\t}"
    )
    new_orig_alpha = (
        "IL_007d:\n"
        "\t{\n"
        "\t\textern float g_OriDefaultTransAlpha;\n"
        "\t\t__this->___OriginalAlpha = g_OriDefaultTransAlpha;\n"
        "\t\treturn;\n"
        "\t}"
    )
    if prev_orig_alpha in content:
        content = content.replace(prev_orig_alpha, new_orig_alpha, 1)
    elif "__this->___OriginalAlpha = g_OriDefaultTransAlpha;" not in content:
        if old_orig_alpha not in content:
            raise RuntimeError("Could not find IL_007d in RendererData__ctor (Assembly-CSharp__25.cpp)")
        content = content.replace(old_orig_alpha, new_orig_alpha, 1)

    # 2. Export OriPort_UpdateTurbulenceGlobals() so OriPortManualPresenter_RenderFrame updates wind/turbulence shader globals
    #    every frame before manual Camera.Render() (since TurbulenceManager.OnRenderObject only fires for its own GameObject's camera).
    turb_helper = (
        "struct OriPortDebugConfig {\n"
        "\tint32_t post_mode; int32_t bloom_blur; int32_t motion_blur; int32_t distortions;\n"
        "\tint32_t alpha_grab_mode; int32_t sanitize_mode; int32_t clamp_depth; float orig_alpha;\n"
        "\tint32_t turbulence; int32_t fixed_hz; float time_scale; int32_t dump_now;\n"
        "\tint32_t panel_open; int32_t exc_render_frame; int32_t exc_dopost; int32_t force_resanitize;\n"
        "};\n"
        "extern OriPortDebugConfig g_OriDebug;\n"
        "IL2CPP_EXTERN_C void OriPort_UpdateTurbulenceGlobals()\n"
        "{\n"
        "\tif (!g_OriDebug.turbulence) return;\n"
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
    old_turb_idx = content.find("struct OriPortDebugConfig {")
    if old_turb_idx == -1:
        old_turb_idx = content.find("IL2CPP_EXTERN_C void OriPort_UpdateTurbulenceGlobals()")
    t_idx = content.find(turb_target)
    if old_turb_idx != -1 and t_idx != -1 and old_turb_idx < t_idx:
        content = content[:old_turb_idx] + content[t_idx:]
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
    #    and export OriPort_DumpPostProcessState + g_OriDebug externs.
    alpha_grab_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void UberAlphaBuffer_SetCurrentAlphaGrab_m69077B2FA1A7F07E8B64E8E4FD884979B6F50E6C"
    old_ext_idx = content.find("#include <stdio.h>\nstruct OriPortDebugConfig")
    if old_ext_idx == -1:
        old_ext_idx = content.find("IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Shader_SetGlobalTexture_m9ECF95F30982225B918E7521B5F2C395CDC3DF16")
    ag_idx = content.find(alpha_grab_decl)
    if old_ext_idx != -1 and ag_idx != -1 and old_ext_idx < ag_idx:
        content = content[:old_ext_idx] + content[ag_idx:]

    ac26_extern_block = (
        "#include <stdio.h>\n"
        "struct OriPortDebugConfig {\n"
        "\tint32_t post_mode; int32_t bloom_blur; int32_t motion_blur; int32_t distortions;\n"
        "\tint32_t alpha_grab_mode; int32_t sanitize_mode; int32_t clamp_depth; float orig_alpha;\n"
        "\tint32_t turbulence; int32_t fixed_hz; float time_scale; int32_t dump_now;\n"
        "\tint32_t panel_open; int32_t exc_render_frame; int32_t exc_dopost; int32_t force_resanitize;\n"
        "};\n"
        "extern OriPortDebugConfig g_OriDebug;\n"
        "IL2CPP_EXTERN_C void OriPort_ApplyAlphaGrabOverride();\n"
        "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void Shader_SetGlobalTexture_m9ECF95F30982225B918E7521B5F2C395CDC3DF16 (String_t* ___0_name, Texture_t791CBB51219779964E0E8A2ED7C1AA5F2C395CDC3DF16_dummy* ___1_value, const RuntimeMethod* method);\n"
    ).replace("Texture_t791CBB51219779964E0E8A2ED7C1AA5F2C395CDC3DF16_dummy", "Texture_t791CBB51219779964E0E8A2ED7C1AA5F92A4A700")
    ac26_extern_block += (
        "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void UberPostProcess_DoCompatibilityPost_m6900914609988B9805C421FA7DDAFFA8B3C083FB (UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC* __this, RenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* ___0_source, RenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* ___1_destination, const RuntimeMethod* method);\n"
        "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR bool UberPostProcess_get_DoMotionBlur_m611984FA0A564898FD6C57461A83201548A330B2 (UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC* __this, const RuntimeMethod* method);\n"
        "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR Vector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 UberPostProcess_get_Speed_mF6F89A4BCD435E117D3A73DE74859E15432350DE_inline (UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC* __this, const RuntimeMethod* method);\n"
        "IL2CPP_EXTERN_C void OriPort_DumpPostProcessState(void* fpVoid)\n"
        "{\n"
        "\tFILE* fp = (FILE*)fpVoid;\n"
        "\tif (fp == NULL) return;\n"
        "\tstatic bool s_init = false;\n"
        "\tif (!s_init)\n"
        "\t{\n"
        "\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_il2cpp_TypeInfo_var);\n"
        "\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);\n"
        "\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&List_1_get_Count_m46D4ED562258FC34C735632E1312C5E45B64FF43_RuntimeMethod_var);\n"
        "\t\ts_init = true;\n"
        "\t}\n"
        "\tfprintf(fp, \"=== UBER POST PROCESS STATE ===\\n\");\n"
        "\ttry\n"
        "\t{\n"
        "\t\til2cpp_codegen_runtime_class_init_inline(UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_il2cpp_TypeInfo_var);\n"
        "\t\til2cpp_codegen_runtime_class_init_inline(Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);\n"
        "\t\tUberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC* inst = ((UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_StaticFields*)il2cpp_codegen_static_fields_for(UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_il2cpp_TypeInfo_var))->___s_instance;\n"
        "\t\tif (inst == NULL || !Object_op_Implicit_m93896EF7D68FA113C42D3FE2BC6F661FC7EF514A((Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)inst, NULL))\n"
        "\t\t{\n"
        "\t\t\tfprintf(fp, \"UberPostProcess.Instance: NULL\\n\\n\");\n"
        "\t\t\treturn;\n"
        "\t\t}\n"
        "\t\tbool doMB = UberPostProcess_get_DoMotionBlur_m611984FA0A564898FD6C57461A83201548A330B2(inst, NULL);\n"
        "\t\tVector3_t24C512C7B96BBABAD472002D0BA2BDA40A5A80B2 spd = UberPostProcess_get_Speed_mF6F89A4BCD435E117D3A73DE74859E15432350DE_inline(inst, NULL);\n"
        "\t\tint32_t ptW = 0, ptH = 0, abW = 0, abH = 0, subCount = 0;\n"
        "\t\tif (inst->___PostTarget != NULL && Object_op_Implicit_m93896EF7D68FA113C42D3FE2BC6F661FC7EF514A((Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)inst->___PostTarget, NULL))\n"
        "\t\t{\n"
        "\t\t\tptW = VirtualFuncInvoker0< int32_t >::Invoke(4, inst->___PostTarget);\n"
        "\t\t\tptH = VirtualFuncInvoker0< int32_t >::Invoke(6, inst->___PostTarget);\n"
        "\t\t}\n"
        "\t\tif (inst->___CurrentAlphaBuffer != NULL && inst->___CurrentAlphaBuffer->___m_alphaBuffer != NULL &&\n"
        "\t\t    Object_op_Implicit_m93896EF7D68FA113C42D3FE2BC6F661FC7EF514A((Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)inst->___CurrentAlphaBuffer->___m_alphaBuffer, NULL))\n"
        "\t\t{\n"
        "\t\t\tabW = VirtualFuncInvoker0< int32_t >::Invoke(4, inst->___CurrentAlphaBuffer->___m_alphaBuffer);\n"
        "\t\t\tabH = VirtualFuncInvoker0< int32_t >::Invoke(6, inst->___CurrentAlphaBuffer->___m_alphaBuffer);\n"
        "\t\t}\n"
        "\t\tList_1_tFC105D2D316B9A77BBADFFAD681A162E1885BEEF* subCams = ((UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_StaticFields*)il2cpp_codegen_static_fields_for(UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_il2cpp_TypeInfo_var))->___s_subCams;\n"
        "\t\tif (subCams != NULL)\n"
        "\t\t{\n"
        "\t\t\tsubCount = List_1_get_Count_m46D4ED562258FC34C735632E1312C5E45B64FF43_inline(subCams, List_1_get_Count_m46D4ED562258FC34C735632E1312C5E45B64FF43_RuntimeMethod_var);\n"
        "\t\t}\n"
        "\t\tfprintf(fp, \"DoMotionBlur(raw)=%d g_OriDebug.motion_blur=%d Speed=(%.3f, %.3f, %.3f) MotionBlurSpread=%.3f\\n\", (int)doMB, g_OriDebug.motion_blur, spd.___x, spd.___y, spd.___z, inst->___MotionBlurSpread);\n"
        "\t\tfprintf(fp, \"PostTarget=%dx%d AlphaBuffer=%dx%d m_doBlur=%d SepBlurSpread=%.3f s_subCams.Count=%d\\n\\n\", ptW, ptH, abW, abH, (int)inst->___m_doBlur, inst->___SepBlurSpread, subCount);\n"
        "\t}\n"
        "\tcatch (Il2CppExceptionWrapper&)\n"
        "\t{\n"
        "\t\tfprintf(fp, \"Exception while dumping UberPostProcess state\\n\\n\");\n"
        "\t}\n"
        "}\n"
    )
    content = content.replace(alpha_grab_decl, ac26_extern_block + alpha_grab_decl, 1)

    old_set_prop = "RenderTexture_SetGlobalShaderProperty_m7BBA88435EDF79EBB5275B3CF84EBEC897EEAAAA(L_2, _stringLiteral38EC5582E0AA27A2D5C239FE57D3F7595653A003, NULL);"
    new_set_prop = "Shader_SetGlobalTexture_m9ECF95F30982225B918E7521B5F2C395CDC3DF16(_stringLiteral38EC5582E0AA27A2D5C239FE57D3F7595653A003, L_2, NULL);"
    if old_set_prop in content:
        content = content.replace(old_set_prop, new_set_prop, 1)

    # Gate motion blur in UberPostProcess_UpdateDirectionalBlur by g_OriDebug.motion_blur
    old_mb_check = (
        "\t\tbool L_0;\n"
        "\t\tL_0 = UberPostProcess_get_DoMotionBlur_m611984FA0A564898FD6C57461A83201548A330B2(__this, NULL);\n"
        "\t\tif (L_0)"
    )
    new_mb_check = (
        "\t\tbool L_0;\n"
        "\t\tL_0 = (g_OriDebug.motion_blur != 0) && UberPostProcess_get_DoMotionBlur_m611984FA0A564898FD6C57461A83201548A330B2(__this, NULL);\n"
        "\t\tif (L_0)"
    )
    if "(g_OriDebug.motion_blur != 0) &&" not in content:
        if old_mb_check not in content:
            raise RuntimeError("Could not find DoMotionBlur check in UberPostProcess_UpdateDirectionalBlur (Assembly-CSharp__26.cpp)")
        content = content.replace(old_mb_check, new_mb_check, 1)

    # 2. Route UberPostProcess.OnRenderImage based on g_OriDebug.post_mode (0=DoCompatibilityPost, 1=DoPost, 2=Raw Blit)
    #    with try/catch exception recovery!
    on_render_image_decl = "IL2CPP_EXTERN_C IL2CPP_METHOD_ATTR void UberPostProcess_OnRenderImage_mD51A4F9A6598D5179C10BE516BE243B1EA51BA53"
    on_render_image_body = (
        "\tstatic bool s_Il2CppMethodInitialized;\n"
        "\tif (!s_Il2CppMethodInitialized)\n"
        "\t{\n"
        "\t\til2cpp_codegen_initialize_runtime_metadata((uintptr_t*)&Graphics_t99CD970FFEA58171C70F54DF0C06D315BD452F2C_il2cpp_TypeInfo_var);\n"
        "\t\ts_Il2CppMethodInitialized = true;\n"
        "\t}\n"
        "\ttry\n"
        "\t{\n"
        "\t\tif (g_OriDebug.post_mode == 0)\n"
        "\t\t{\n"
        "\t\t\tUberPostProcess_DoCompatibilityPost_m6900914609988B9805C421FA7DDAFFA8B3C083FB(__this, ___0_source, ___1_destination, NULL);\n"
        "\t\t}\n"
        "\t\telse if (g_OriDebug.post_mode == 2)\n"
        "\t\t{\n"
        "\t\t\til2cpp_codegen_runtime_class_init_inline(Graphics_t99CD970FFEA58171C70F54DF0C06D315BD452F2C_il2cpp_TypeInfo_var);\n"
        "\t\t\tGraphics_Blit_m8D99E16B74C7D3C8F79F4F142C59DB6B38114504(___0_source, ___1_destination, NULL);\n"
        "\t\t}\n"
        "\t\telse\n"
        "\t\t{\n"
        "\t\t\tUberPostProcess_DoPost_m6A2D0C46B4E566F7496AC41A7502DA9E36305DD1(__this, ___0_source, ___1_destination, NULL);\n"
        "\t\t}\n"
        "\t}\n"
        "\tcatch (Il2CppExceptionWrapper&)\n"
        "\t{\n"
        "\t\tg_OriDebug.exc_dopost++;\n"
        "\t\til2cpp_codegen_runtime_class_init_inline(Graphics_t99CD970FFEA58171C70F54DF0C06D315BD452F2C_il2cpp_TypeInfo_var);\n"
        "\t\tGraphics_Blit_m8D99E16B74C7D3C8F79F4F142C59DB6B38114504(___0_source, ___1_destination, NULL);\n"
        "\t}\n"
        "\treturn;"
    )
    content = replace_func_body(content, on_render_image_decl, on_render_image_body)

    # 3. In UberPostProcess.DoPost:
    #    - Initialize RenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27_il2cpp_TypeInfo_var metadata
    #    - Ensure __this->___PostTarget is allocated/resized to match ___0_source width/height
    #    - Gate UberAlphaBuffer, Bloom/BlurPingPong, and RenderDistortions by g_OriDebug flags
    #    - Null-check s_subCams elements and UberUIPostProcess.Instance!
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

    old_alpha_buf = (
        "\t\tUberAlphaBuffer_t556A54B07009C70BD46B22D94E06B3CA37D9DE64* L_8 = __this->___CurrentAlphaBuffer;\n"
        "\t\tRenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* L_9 = ___0_source;\n"
        "\t\tMaterial_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* L_10 = __this->___m_material;\n"
        "\t\tNullCheck(L_8);\n"
        "\t\tUberAlphaBuffer_OnRenderImage_m4FBEBF5BDF5842C0C895B09E10EE7BDF6F90FD25(L_8, L_9, L_10, NULL);\n"
        "\t\tUberAlphaBuffer_t556A54B07009C70BD46B22D94E06B3CA37D9DE64* L_11 = __this->___CurrentAlphaBuffer;\n"
        "\t\tNullCheck(L_11);\n"
        "\t\tUberAlphaBuffer_SetCurrentAlphaGrab_m69077B2FA1A7F07E8B64E8E4FD884979B6F50E6C(L_11, NULL);"
    )
    new_alpha_buf = (
        "\t\tif (g_OriDebug.alpha_grab_mode == 0 && __this->___CurrentAlphaBuffer != NULL)\n"
        "\t\t{\n"
        "\t\t\tUberAlphaBuffer_t556A54B07009C70BD46B22D94E06B3CA37D9DE64* L_8 = __this->___CurrentAlphaBuffer;\n"
        "\t\t\tRenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* L_9 = ___0_source;\n"
        "\t\t\tMaterial_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* L_10 = __this->___m_material;\n"
        "\t\t\tUberAlphaBuffer_OnRenderImage_m4FBEBF5BDF5842C0C895B09E10EE7BDF6F90FD25(L_8, L_9, L_10, NULL);\n"
        "\t\t\tUberAlphaBuffer_SetCurrentAlphaGrab_m69077B2FA1A7F07E8B64E8E4FD884979B6F50E6C(L_8, NULL);\n"
        "\t\t}\n"
        "\t\telse\n"
        "\t\t{\n"
        "\t\t\tOriPort_ApplyAlphaGrabOverride();\n"
        "\t\t}"
    )
    if "if (g_OriDebug.alpha_grab_mode == 0 && __this->___CurrentAlphaBuffer != NULL)" not in content:
        if old_alpha_buf not in content:
            raise RuntimeError("Could not find UberAlphaBuffer block in UberPostProcess_DoPost (Assembly-CSharp__26.cpp)")
        content = content.replace(old_alpha_buf, new_alpha_buf, 1)

    old_bloom_blur = (
        "\t\tUberGaussianBlur_BlurPingPong_m09ED73A2799241F6D6FBB8FEE4A0B6355A245415(L_25, L_26, 2, L_27, NULL);"
    )
    new_bloom_blur = (
        "\t\tif (g_OriDebug.bloom_blur != 0)\n"
        "\t\t{\n"
        "\t\t\tUberGaussianBlur_BlurPingPong_m09ED73A2799241F6D6FBB8FEE4A0B6355A245415(L_25, L_26, 2, L_27, NULL);\n"
        "\t\t}"
    )
    if "if (g_OriDebug.bloom_blur != 0)" not in content:
        if old_bloom_blur not in content:
            raise RuntimeError("Could not find BlurPingPong block in UberPostProcess_DoPost (Assembly-CSharp__26.cpp)")
        content = content.replace(old_bloom_blur, new_bloom_blur, 1)

    old_distort = (
        "\t\tUberPostProcess_RenderDistortions_m3BE2D6EAC0617F3D838E044B45E378BC59B03EE6(__this, L_36, NULL);\n"
        "\t\tUberPostProcess_SetInterestZones_m5C65FA28BC9A7B8BDA282741083C04A9AA772908(__this, NULL);\n"
        "\t\tMaterial_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* L_37 = __this->___m_material;\n"
        "\t\til2cpp_codegen_runtime_class_init_inline(UberPostCacheIds_t9EBFAA44CA219ABF30A1382159A47EDE00B1FC26_il2cpp_TypeInfo_var);\n"
        "\t\tint32_t L_38 = ((UberPostCacheIds_t9EBFAA44CA219ABF30A1382159A47EDE00B1FC26_StaticFields*)il2cpp_codegen_static_fields_for(UberPostCacheIds_t9EBFAA44CA219ABF30A1382159A47EDE00B1FC26_il2cpp_TypeInfo_var))->___ColorBuffer;\n"
        "\t\tRenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* L_39 = V_1;\n"
        "\t\tNullCheck(L_37);\n"
        "\t\tMaterial_SetTexture_mA9F8461850AAB88F992E9C6FA6F24C2E050B83FD(L_37, L_38, L_39, NULL);\n"
        "\t\tUberPostProcess_UpdateDirectionalBlur_mCEAB8032282C675F547E62E03AF9402F54B8D26C(__this, NULL);\n"
        "\t\tRenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* L_40 = ___0_source;\n"
        "\t\tRenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* L_41 = __this->___PostTarget;\n"
        "\t\tMaterial_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* L_42 = __this->___m_material;\n"
        "\t\til2cpp_codegen_runtime_class_init_inline(Graphics_t99CD970FFEA58171C70F54DF0C06D315BD452F2C_il2cpp_TypeInfo_var);\n"
        "\t\tGraphics_Blit_m1875691D6AAA8CF8EDE8508538714CF895E36779(L_40, L_41, L_42, 0, NULL);\n"
        "\t\tbool L_43 = __this->___m_doBlur;\n"
        "\t\tif (!L_43)"
    )
    new_distort = (
        "\t\tif (g_OriDebug.distortions != 0)\n"
        "\t\t{\n"
        "\t\t\tUberPostProcess_RenderDistortions_m3BE2D6EAC0617F3D838E044B45E378BC59B03EE6(__this, L_36, NULL);\n"
        "\t\t}\n"
        "\t\tUberPostProcess_SetInterestZones_m5C65FA28BC9A7B8BDA282741083C04A9AA772908(__this, NULL);\n"
        "\t\tMaterial_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* L_37 = __this->___m_material;\n"
        "\t\til2cpp_codegen_runtime_class_init_inline(UberPostCacheIds_t9EBFAA44CA219ABF30A1382159A47EDE00B1FC26_il2cpp_TypeInfo_var);\n"
        "\t\tint32_t L_38 = ((UberPostCacheIds_t9EBFAA44CA219ABF30A1382159A47EDE00B1FC26_StaticFields*)il2cpp_codegen_static_fields_for(UberPostCacheIds_t9EBFAA44CA219ABF30A1382159A47EDE00B1FC26_il2cpp_TypeInfo_var))->___ColorBuffer;\n"
        "\t\tRenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* L_39 = V_1;\n"
        "\t\tNullCheck(L_37);\n"
        "\t\tMaterial_SetTexture_mA9F8461850AAB88F992E9C6FA6F24C2E050B83FD(L_37, L_38, L_39, NULL);\n"
        "\t\tUberPostProcess_UpdateDirectionalBlur_mCEAB8032282C675F547E62E03AF9402F54B8D26C(__this, NULL);\n"
        "\t\tRenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* L_40 = ___0_source;\n"
        "\t\tRenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* L_41 = __this->___PostTarget;\n"
        "\t\tMaterial_t18053F08F347D0DCA5E1140EC7EC4533DD8A14E3* L_42 = __this->___m_material;\n"
        "\t\til2cpp_codegen_runtime_class_init_inline(Graphics_t99CD970FFEA58171C70F54DF0C06D315BD452F2C_il2cpp_TypeInfo_var);\n"
        "\t\tGraphics_Blit_m1875691D6AAA8CF8EDE8508538714CF895E36779(L_40, L_41, L_42, 0, NULL);\n"
        "\t\tbool L_43 = (g_OriDebug.bloom_blur != 0) && __this->___m_doBlur;\n"
        "\t\tif (!L_43)"
    )
    if "if (g_OriDebug.distortions != 0)" not in content:
        if old_distort not in content:
            raise RuntimeError("Could not find RenderDistortions block in UberPostProcess_DoPost (Assembly-CSharp__26.cpp)")
        content = content.replace(old_distort, new_distort, 1)

    old_subcams = (
        "IL_0175:\n"
        "\t{\n"
        "\t\til2cpp_codegen_runtime_class_init_inline(UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_il2cpp_TypeInfo_var);\n"
        "\t\tList_1_tFC105D2D316B9A77BBADFFAD681A162E1885BEEF* L_53 = ((UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_StaticFields*)il2cpp_codegen_static_fields_for(UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_il2cpp_TypeInfo_var))->___s_subCams;\n"
        "\t\tint32_t L_54 = V_5;\n"
        "\t\tNullCheck(L_53);\n"
        "\t\tUberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC* L_55;\n"
        "\t\tL_55 = List_1_get_Item_mC77DEE349AFB153411AF72E660D79EDC47687340(L_53, L_54, List_1_get_Item_mC77DEE349AFB153411AF72E660D79EDC47687340_RuntimeMethod_var);\n"
        "\t\tNullCheck(L_55);\n"
        "\t\tGameObject_t76FEDD663AB33C991A9C9A23129337651094216F* L_56;\n"
        "\t\tL_56 = Component_get_gameObject_m57AEFBB14DB39EC476F740BA000E170355DE691B(L_55, NULL);\n"
        "\t\tNullCheck(L_56);\n"
        "\t\tbool L_57;\n"
        "\t\tL_57 = GameObject_get_activeInHierarchy_m49250F4F168DCC5388D5BE4F6A5681386907B109(L_56, NULL);\n"
        "\t\tif (!L_57)\n"
        "\t\t{\n"
        "\t\t\tgoto IL_01e5;\n"
        "\t\t}\n"
        "\t}\n"
        "\t{\n"
        "\t\til2cpp_codegen_runtime_class_init_inline(UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_il2cpp_TypeInfo_var);\n"
        "\t\tList_1_tFC105D2D316B9A77BBADFFAD681A162E1885BEEF* L_58 = ((UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_StaticFields*)il2cpp_codegen_static_fields_for(UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_il2cpp_TypeInfo_var))->___s_subCams;\n"
        "\t\tint32_t L_59 = V_5;\n"
        "\t\tNullCheck(L_58);\n"
        "\t\tUberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC* L_60;\n"
        "\t\tL_60 = List_1_get_Item_mC77DEE349AFB153411AF72E660D79EDC47687340(L_58, L_59, List_1_get_Item_mC77DEE349AFB153411AF72E660D79EDC47687340_RuntimeMethod_var);\n"
        "\t\tNullCheck(L_60);\n"
        "\t\tCamera_tA92CC927D7439999BC82DBEDC0AA45B470F9E184* L_61 = L_60->___Camera;\n"
        "\t\tCamera_tA92CC927D7439999BC82DBEDC0AA45B470F9E184* L_62 = L_61;\n"
        "\t\tRenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* L_63 = __this->___PostTarget;\n"
        "\t\tNullCheck(L_62);"
    )
    new_subcams = (
        "IL_0175:\n"
        "\t{\n"
        "\t\til2cpp_codegen_runtime_class_init_inline(UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_il2cpp_TypeInfo_var);\n"
        "\t\til2cpp_codegen_runtime_class_init_inline(Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C_il2cpp_TypeInfo_var);\n"
        "\t\tList_1_tFC105D2D316B9A77BBADFFAD681A162E1885BEEF* L_53 = ((UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_StaticFields*)il2cpp_codegen_static_fields_for(UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_il2cpp_TypeInfo_var))->___s_subCams;\n"
        "\t\tif (L_53 == NULL) goto IL_01e5;\n"
        "\t\tint32_t L_54 = V_5;\n"
        "\t\tUberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC* L_55 = List_1_get_Item_mC77DEE349AFB153411AF72E660D79EDC47687340(L_53, L_54, List_1_get_Item_mC77DEE349AFB153411AF72E660D79EDC47687340_RuntimeMethod_var);\n"
        "\t\tif (L_55 == NULL || !Object_op_Implicit_m93896EF7D68FA113C42D3FE2BC6F661FC7EF514A((Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)L_55, NULL)) goto IL_01e5;\n"
        "\t\tGameObject_t76FEDD663AB33C991A9C9A23129337651094216F* L_56 = Component_get_gameObject_m57AEFBB14DB39EC476F740BA000E170355DE691B(L_55, NULL);\n"
        "\t\tif (L_56 == NULL || !GameObject_get_activeInHierarchy_m49250F4F168DCC5388D5BE4F6A5681386907B109(L_56, NULL))\n"
        "\t\t{\n"
        "\t\t\tgoto IL_01e5;\n"
        "\t\t}\n"
        "\t}\n"
        "\t{\n"
        "\t\til2cpp_codegen_runtime_class_init_inline(UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_il2cpp_TypeInfo_var);\n"
        "\t\tList_1_tFC105D2D316B9A77BBADFFAD681A162E1885BEEF* L_58 = ((UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_StaticFields*)il2cpp_codegen_static_fields_for(UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_il2cpp_TypeInfo_var))->___s_subCams;\n"
        "\t\tint32_t L_59 = V_5;\n"
        "\t\tUberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC* L_60 = List_1_get_Item_mC77DEE349AFB153411AF72E660D79EDC47687340(L_58, L_59, List_1_get_Item_mC77DEE349AFB153411AF72E660D79EDC47687340_RuntimeMethod_var);\n"
        "\t\tCamera_tA92CC927D7439999BC82DBEDC0AA45B470F9E184* L_62 = (L_60 != NULL) ? L_60->___Camera : NULL;\n"
        "\t\tif (L_62 == NULL || !Object_op_Implicit_m93896EF7D68FA113C42D3FE2BC6F661FC7EF514A((Object_tC12DECB6760A7F2CBF65D9DCF18D044C2D97152C*)L_62, NULL)) goto IL_01e5;\n"
        "\t\tRenderTexture_tBA90C4C3AD9EECCFDDCC632D97C29FAB80D60D27* L_63 = __this->___PostTarget;"
    )
    if "if (L_53 == NULL) goto IL_01e5;" not in content:
        if old_subcams not in content:
            raise RuntimeError("Could not find IL_0175 s_subCams block in UberPostProcess_DoPost (Assembly-CSharp__26.cpp)")
        content = content.replace(old_subcams, new_subcams, 1)

    old_subcams_end = (
        "\t\tList_1_tFC105D2D316B9A77BBADFFAD681A162E1885BEEF* L_73 = ((UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_StaticFields*)il2cpp_codegen_static_fields_for(UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_il2cpp_TypeInfo_var))->___s_subCams;\n"
        "\t\tNullCheck(L_73);\n"
        "\t\tint32_t L_74;\n"
        "\t\tL_74 = List_1_get_Count_m46D4ED562258FC34C735632E1312C5E45B64FF43_inline(L_73, List_1_get_Count_m46D4ED562258FC34C735632E1312C5E45B64FF43_RuntimeMethod_var);"
    )
    new_subcams_end = (
        "\t\tList_1_tFC105D2D316B9A77BBADFFAD681A162E1885BEEF* L_73 = ((UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_StaticFields*)il2cpp_codegen_static_fields_for(UberPostProcess_t4FB6B8834D1576B2D9DE80137E588F45AA9D1CCC_il2cpp_TypeInfo_var))->___s_subCams;\n"
        "\t\tint32_t L_74 = (L_73 != NULL) ? List_1_get_Count_m46D4ED562258FC34C735632E1312C5E45B64FF43_inline(L_73, List_1_get_Count_m46D4ED562258FC34C735632E1312C5E45B64FF43_RuntimeMethod_var) : 0;"
    )
    if "(L_73 != NULL) ?" not in content:
        if old_subcams_end not in content:
            raise RuntimeError("Could not find IL_01eb s_subCams Count block in UberPostProcess_DoPost (Assembly-CSharp__26.cpp)")
        content = content.replace(old_subcams_end, new_subcams_end, 1)

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
