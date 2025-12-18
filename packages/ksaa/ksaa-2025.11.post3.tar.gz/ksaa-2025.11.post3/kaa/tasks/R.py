
from kaa.common import sprite_path
from kotonebot.backend.core import Image, HintBox, HintPoint



class Common:
    
    ButtonClose = Image(path=sprite_path(r"2747e1e6-c351-49f9-a1ee-67ac63b4641b.png"), name="button_close.png")

    ButtonCompletion = Image(path=sprite_path(r"cebd1ab2-a8ee-4d1c-96b8-bd1de32aec46.png"), name="button_completion.png")

    ButtonConfirm = Image(path=sprite_path(r"86cbaa8e-3423-4d91-8b71-71adb444e99f.png"), name="button_confirm.png")

    ButtonConfirmNoIcon = Image(path=sprite_path(r"361ff50a-6b64-4abb-8971-1e995ada74e6.png"), name="button_confirm_no_icon.png")

    ButtonContest = Image(path=sprite_path(r"015b5779-cadf-4024-85b1-d0c55f9f46f1.png"), name="button_contest.png")

    ButtonEnd = Image(path=sprite_path(r"25be2fc1-407e-4c39-99a0-332083653123.png"), name="button_end.png")

    ButtonHome = Image(path=sprite_path(r"2e758a0f-30fa-4177-bd2e-b65d6939254d.png"), name="button_home.png")

    ButtonIconArrowShort = Image(path=sprite_path(r"4b8a47a1-ef79-4f5e-b52b-d2251404b718.png"), name="button_icon_arrow_short.png")

    ButtonIconArrowShortDisabled = Image(path=sprite_path(r"ef3ed72e-b7ee-49ef-a880-c42d01b71f98.png"), name="button_icon_arrow_short_disabled.png")

    ButtonIconCheckMark = Image(path=sprite_path(r"ca0c340b-a4e7-4596-ae3a-b62da71baadd.png"), name="button_icon_check_mark.png")

    ButtonIconClose = Image(path=sprite_path(r"8bf0f15f-c45b-4f3d-b9ca-1bcc73e06779.png"), name="button_icon_close.png")

    ButtonIdol = Image(path=sprite_path(r"b2d9df4f-c78c-4ae0-aa75-27397296665f.png"), name="button_idol.png")

    ButtonIdolSupportCard = Image(path=sprite_path(r"f32cc10e-14f1-4420-9373-f8a4aa31c82c.png"), name="button_idol_support_card.png")

    ButtonNext = Image(path=sprite_path(r"e32ba2b8-996f-429b-afb1-5ea712ca9285.png"), name="button_next.png")

    ButtonNextNoIcon = Image(path=sprite_path(r"f6db0f1f-b429-4a7e-b0be-7377a2c8f3b8.png"), name="button_next_no_icon.png")

    ButtonRetry = Image(path=sprite_path(r"db545bdc-0829-48e4-82f5-e95fd34bc1f9.png"), name="button_retry.png")

    ButtonSelect = Image(path=sprite_path(r"4a70897f-0a9b-4b76-8ec1-873cbcfb3c9f.png"), name="button_select.png")

    ButtonStart = Image(path=sprite_path(r"29059030-a083-4884-92c9-eec3dfe0e4ab.png"), name="button_start.png")

    ButtonToolbarMenu = Image(path=sprite_path(r"922bfd40-3554-4de7-a09a-0d79acfd377f.png"), name="button_toolbar_menu.png")

    CheckboxUnchecked = Image(path=sprite_path(r"7c787834-cc44-404b-a1ce-1c5af6a6f577.png"), name="checkbox_unchecked.png")

    ShopPackButton = Image(path=sprite_path(r"5c49d3b3-656e-4c8c-ae1a-9b0209b9dcc3.png"), name="商店礼包页面按钮")

    ShopPackRedDot = HintBox(x1=650, y1=660, x2=687, y2=697, source_resolution=(720, 1280))

    ButtonToolbarHome = Image(path=sprite_path(r"7b5c8883-a1f9-4ce9-bd84-26668577dfc6.png"), name="工具栏的主页按钮")

    ButtonToolbarBack = Image(path=sprite_path(r"41904062-e218-4b28-972a-b5cfcd058d2c.png"), name="工具栏的返回按钮")

    TextGameUpdate = Image(path=sprite_path(r"b827fa25-fa83-4ce6-b21f-1aebdc928bd9.png"), name="text_game_update.png")

    TextNetworkError = Image(path=sprite_path(r"267677d2-c40b-4d6b-8769-3c42a7cca3e7.png"), name="text_network_error.png")

    TextFastforwardCommuDialogTitle = Image(path=sprite_path(r"50e23c8a-7ba2-4c9c-9cfb-196c260fa1d5.png"), name="早送り確認")

    ButtonCommuSkip = Image(path=sprite_path(r"f1f21925-3e22-4dd1-b53b-bb52bcf26c2b.png"), name="跳过交流按钮")

    ButtonCommuFastforward = Image(path=sprite_path(r"f6ca6bd3-543f-4779-8367-c5c883f04b95.png"), name="快进交流按钮")

    ButtonOK = Image(path=sprite_path(r"8424ecdd-8857-4764-9fd0-d4bfa440c128.png"), name="OK 按钮")

    ButtonSelect2 = Image(path=sprite_path(r"5ebcde3b-f0fd-4e5d-b3de-ada8f0b5e03b.png"), name="選択する")

    TextSkipCommuComfirmation = Image(path=sprite_path(r"4d78add6-1027-4939-bb51-f99fca7db2ce.png"), name="跳过未读交流确认对话框标题")

    IconButtonCheck = Image(path=sprite_path(r"fad5eec2-5fd5-412f-9abb-987a3087dc54.png"), name="按钮✓图标")

    IconButtonCross = Image(path=sprite_path(r"bc7155ac-18c9-4335-9ec2-c8762d37a057.png"), name="按钮×图标")


    pass
class Daily:
    
    ButonLinkData = Image(path=sprite_path(r"7322ad76-3a6c-4d0a-a82c-23a884d1e4d2.png"), name="buton_link_data.png")

    ButtonAssignmentPartial = Image(path=sprite_path(r"ce2a6f51-93d2-4825-9ba1-6a628ae7e423.png"), name="button_assignment_partial.png")

    ButtonClaimAllNoIcon = Image(path=sprite_path(r"d2babef2-f14b-4200-a13e-2c080cd1d659.png"), name="button_claim_all_no_icon.png")

    ButtonClubCollectReward = Image(path=sprite_path(r"3a8172a7-f7f9-4ed6-aa82-166356fb3216.png"), name="button_club_collect_reward.png")

    ButtonClubSendGift = Image(path=sprite_path(r"5fe81be9-4a51-4d65-b288-60d69a7b38f9.png"), name="button_club_send_gift.png")

    ButtonClubSendGiftNext = Image(path=sprite_path(r"092825be-4bd4-4efb-940c-296cbec4a0ff.png"), name="button_club_send_gift_next.png")

    ButtonContestChallenge = Image(path=sprite_path(r"27834c18-365c-4c88-885a-edf0e5fa92a9.png"), name="button_contest_challenge.png")

    ButtonContestChallengeStart = Image(path=sprite_path(r"119d3a35-68fb-410d-9422-3b35b611e5a9.png"), name="button_contest_challenge_start.png")

    ButtonContestRanking = Image(path=sprite_path(r"c735fbac-b584-4ffc-a782-6f606ff68eb4.png"), name="button_contest_ranking.png")

    ButtonContestStart = Image(path=sprite_path(r"a37ca8e8-9145-49eb-bf5c-9741de14b7a4.png"), name="button_contest_start.png")

    ButtonDailyShop = Image(path=sprite_path(r"6d02d06b-0faa-4d70-8671-8bc04bf1c57f.png"), name="button_daily_shop.png")

    ButtonHomeCurrent = Image(path=sprite_path(r"e321228b-82e7-49d3-b488-74b2a176c8cf.png"), name="button_home_current.png")

    ButtonIconPass = Image(path=sprite_path(r"c78fe004-f838-4e95-9b3f-672274af4741.png"), name="button_icon_pass.png")

    ButtonIconSkip = Image(path=sprite_path(r"109ef0c7-5169-40e3-93e0-a6d224cc6223.png"), name="button_icon_skip.png")

    ButtonMission = Image(path=sprite_path(r"66a7a951-2171-4f29-96a7-4bac35c69d89.png"), name="button_mission.png")

    ButtonPass = Image(path=sprite_path(r"0defd088-91db-4a2c-827a-6ccc94ba4911.png"), name="button_pass.png")

    ButtonPassClaim = Image(path=sprite_path(r"c1365964-fb44-41b7-aa4f-5b3c98a32d37.png"), name="button_pass_claim.png")

    ButtonPresentsPartial = Image(path=sprite_path(r"0db54886-41a9-41c8-9941-545e4b3beaef.png"), name="button_presents_partial.png")

    ButtonProduce = Image(path=sprite_path(r"8d7de096-a4e9-469c-8b36-b55f875ce702.png"), name="button_produce.png")

    ButtonShop = Image(path=sprite_path(r"1a78973f-3cac-4120-a194-70d90297f449.png"), name="button_shop.png")

    ButtonShopCapsuleToys = Image(path=sprite_path(r"6728ad4d-3153-49e6-b1d4-15df488de9ec.png"), name="button_shop_capsule_toys.png")

    ButtonShopCapsuleToysDraw = Image(path=sprite_path(r"bdbd1b83-6c8d-4a87-9124-9d9e2da5ad2a.png"), name="button_shop_capsule_toys_draw.png")

    ButtonShopCountAdd = Image(path=sprite_path(r"8117ea59-2722-4a68-b593-017464aa594d.png"), name="button_shop_count_add.png")

    ButtonShopCountAddDisabled = Image(path=sprite_path(r"8dd0fe2d-9d93-4226-a416-ac5ab9def5b1.png"), name="button_shop_count_add_disabled.png")

    ButtonSupportCardUpgrade = Image(path=sprite_path(r"dd4c404b-2f05-481b-9a09-b816c66f4cbf.png"), name="button_support_card_upgrade.png")

    ButtonRefreshMoneyShop = Image(path=sprite_path(r"81c97cd3-df53-44d3-bf3d-1eb4dc67b62a.png"), name="リスト更新：1回無料")

    IconTitleDailyShop = Image(path=sprite_path(r"e9ee330d-dfca-440e-8b8c-0a3b4e8c8730.png"), name="日常商店标题图标")

    BoxHomeAssignment = HintBox(x1=33, y1=650, x2=107, y2=746, source_resolution=(720, 1280))

    BoxHomeAP = HintBox(x1=291, y1=4, x2=500, y2=82, source_resolution=(720, 1280))

    BoxHomeJewel = HintBox(x1=500, y1=7, x2=703, y2=82, source_resolution=(720, 1280))

    BoxHomeActivelyFunds = HintBox(x1=29, y1=530, x2=109, y2=633, source_resolution=(720, 1280))

    IconAssignKouchou = Image(path=sprite_path(r"91786ae8-df00-40e1-958c-4bf92119018b.png"), name="icon_assign_kouchou.png")

    IconAssignMiniLive = Image(path=sprite_path(r"7922ffd6-1958-4a35-b4fe-400d824dc7e5.png"), name="icon_assign_mini_live.png")

    IconAssignOnlineLive = Image(path=sprite_path(r"a472bad4-5d25-4ea4-af80-875ed46c0c40.png"), name="icon_assign_online_live.png")

    IconAssignTitle = Image(path=sprite_path(r"4b3f0f43-d332-4051-acec-994f722728f2.png"), name="icon_assign_title.png")

    IconMenuClub = Image(path=sprite_path(r"df092ec2-cc43-4f62-902f-9c06523186cb.png"), name="icon_menu_club.png")

    IconShopAp = Image(path=sprite_path(r"2a693e8d-70a2-4176-b29a-5a9c42f17168.png"), name="icon_shop_ap.png")

    IconShopMoney = Image(path=sprite_path(r"f3ffefce-c2f3-4f22-9fe6-02a130c24d8a.png"), name="icon_shop_money.png")

    IconShopTitle = Image(path=sprite_path(r"02f9ea01-1a30-47a7-814b-b81afb07add7.png"), name="icon_shop_title.png")

    IconTitleAssign = Image(path=sprite_path(r"8862d215-8a42-4bd4-931e-61059e5925f2.png"), name="icon_title_assign.png")

    IconTitlePass = Image(path=sprite_path(r"fad39378-12f3-4f7c-8200-0a7a2ec9440a.png"), name="icon_title_pass.png")

    BoxApkUpdateDialogTitle = HintBox(x1=26, y1=905, x2=342, y2=967, source_resolution=(720, 1280))

    ButtonAssignmentShortenTime = Image(path=sprite_path(r"1652f06a-5417-49ef-8949-4854772d9ab7.png"), name="工作页面 短缩 时间")

    class Club:
        
        NoteRequestHintBox = HintBox(x1=314, y1=1071, x2=450, y2=1099, source_resolution=(720, 1280))
    
    
        pass
    TextRoadToIdol = Image(path=sprite_path(r"4503db6b-7224-4b81-9971-e7cfa56e10f2.png"), name="文字「アイドルへの道」")

    PointContest = HintPoint(x=492, y=878)

    PointDissmissContestReward = HintPoint(x=604, y=178)

    TextDateChangeDialogConfirmButton = Image(path=sprite_path(r"eaad330d-4e50-4b55-be2c-8da0f72764d9.png"), name="日期变更对话框的确认按钮")

    TextDateChangeDialog = Image(path=sprite_path(r"9483fae5-3a72-4684-9403-d25d2c602d3d.png"), name="日期变更对话框")

    BoxMissonTabs = HintBox(x1=11, y1=929, x2=703, y2=1030, source_resolution=(720, 1280))

    class CapsuleToys:
        
        NextPageStartPoint = HintPoint(x=360, y=1167)
    
        NextPageEndPoint = HintPoint(x=362, y=267)
    
        IconTitle = Image(path=sprite_path(r"2bd6fe88-99fa-443d-8e42-bb3de5881213.png"), name="日常 扭蛋 页面标题图标")
    
        SliderStartPoint = HintPoint(x=476, y=898)
    
        SliderEndPoint = HintPoint(x=230, y=898)
    
    
        pass
    TextDefaultExchangeCountChangeDialog = Image(path=sprite_path(r"de325534-3fd3-480a-9eb8-eb47960a753a.png"), name="商店默认购买次数改变对话框")

    TextShopItemPurchased = Image(path=sprite_path(r"5d36b880-7b3f-49b1-a018-7de59867d376.png"), name="交換しました")

    TextShopItemSoldOut = Image(path=sprite_path(r"24dc7158-036c-4a66-9280-e934f470be53.png"), name="交換済みです")

    class SupportCard:
        
        DragDownStartPoint = HintPoint(x=357, y=872)
    
        DragDownEndPoint = HintPoint(x=362, y=194)
    
        TargetSupportCard = HintPoint(x=138, y=432)
    
    
        pass
    WeeklyFreePack = Image(path=sprite_path(r"ae4742aa-acda-442d-bf73-b3fe7b66e85c.png"), name="每周免费礼包购买按钮")

    TextActivityFundsMax = Image(path=sprite_path(r"151190e3-e49b-4505-a09e-d09a2a3d1e19.png"), name="text_activity_funds_max.png")

    TextAssignmentCompleted = Image(path=sprite_path(r"cb167a0e-0925-4793-9116-410ab08a1386.png"), name="text_assignment_completed.png")

    TextContest = Image(path=sprite_path(r"db5226f6-c5f5-4607-8183-eb007924e4f1.png"), name="text_contest.png")

    TextContestLastOngoing = Image(path=sprite_path(r"c620eee0-b4af-4125-8739-5524130a8011.png"), name="text_contest_last_ongoing.png")

    TextContestNoMemory = Image(path=sprite_path(r"f5c48b06-74ca-4d19-8e8c-ae029051a23c.png"), name="text_contest_no_memory.png")

    TextContestOverallStats = Image(path=sprite_path(r"391e6937-4348-4dbe-aeaf-73a997009c39.png"), name="text_contest_overall_stats.png")

    TextShopRecommended = Image(path=sprite_path(r"cb27515b-50d6-47cb-b239-8462c575e5ef.png"), name="text_shop_recommended.png")

    TextTabShopAp = Image(path=sprite_path(r"7c035a9f-6aad-477a-b4bb-3cddeb47c346.png"), name="text_tab_shop_ap.png")


    pass
class Shop:
    
    ItemLessonNote = Image(path=sprite_path(r"0949c622-9067-4f0d-bac2-3f938a1d2ed2.png"), name="レッスンノート")

    ItemVeteranNote = Image(path=sprite_path(r"b2af59e9-60e3-4d97-8c72-c7ba092113a3.png"), name="ベテランノート")

    ItemSupportEnhancementPt = Image(path=sprite_path(r"835489e2-b29b-426c-b4c9-3bb9f8eb6195.png"), name="サポート強化Pt 支援强化Pt")

    ItemSenseNoteVocal = Image(path=sprite_path(r"c5b7d67e-7260-4f08-a0e9-4d31ce9bbecf.png"), name="センスノート（ボーカル）感性笔记（声乐）")

    ItemSenseNoteDance = Image(path=sprite_path(r"0f7d581d-cea3-4039-9205-732e4cd29293.png"), name="センスノート（ダンス）感性笔记（舞蹈）")

    ItemSenseNoteVisual = Image(path=sprite_path(r"d3cc3323-51af-4882-ae12-49e7384b746d.png"), name="センスノート（ビジュアル）感性笔记（形象）")

    ItemLogicNoteVocal = Image(path=sprite_path(r"a1df3af1-a3e7-4521-a085-e4dc3cd1cc57.png"), name="ロジックノート（ボーカル）理性笔记（声乐）")

    ItemLogicNoteDance = Image(path=sprite_path(r"a9fcaf04-0c1f-4b0f-bb5b-ede9da96180f.png"), name="ロジックノート（ダンス）理性笔记（舞蹈）")

    ItemLogicNoteVisual = Image(path=sprite_path(r"c3f536d6-a04a-4651-b3f9-dd2c22593f7f.png"), name="ロジックノート（ビジュアル）理性笔记（形象）")

    ItemAnomalyNoteVocal = Image(path=sprite_path(r"eef25cf9-afd0-43b1-b9c5-fbd997bd5fe0.png"), name="アノマリーノート（ボーカル）非凡笔记（声乐）")

    ItemAnomalyNoteDance = Image(path=sprite_path(r"df991b42-ed8e-4f2c-bf0c-aa7522f147b6.png"), name="アノマリーノート（ダンス）非凡笔记（舞蹈）")

    ItemAnomalyNoteVisual = Image(path=sprite_path(r"9340b854-025c-40da-9387-385d38433bef.png"), name="アノマリーノート（ビジュアル）非凡笔记（形象）")

    ItemRechallengeTicket = Image(path=sprite_path(r"ea1ba124-9cb3-4427-969a-bacd47e7d920.png"), name="再挑戦チケット 重新挑战券")

    ItemRecordKey = Image(path=sprite_path(r"1926f2f9-4bd7-48eb-9eba-28ec4efb0606.png"), name="記録の鍵  解锁交流的物品")

    class IdolPiece:
        
        花海咲季_FightingMyWay = Image(path=sprite_path(r"3942ae40-7f22-412c-aebe-4b064f68db9b.png"), name="")
    
        月村手毬_LunaSayMaybe = Image(path=sprite_path(r"185f7838-92a7-460b-9340-f60858948ce9.png"), name="")
    
        藤田ことね_世界一可愛い私  = Image(path=sprite_path(r"cb3d0ca7-8d14-408a-a2f5-2e25f7b86d6c.png"), name="")
    
        花海佑芽_TheRollingRiceball = Image(path=sprite_path(r"213016c2-c3a2-43d8-86a3-ab4d27666ced.png"), name="")
    
        葛城リーリヤ_白線 = Image(path=sprite_path(r"cc60b509-2ed5-493d-bb9f-333c6d2a6006.png"), name="")
    
        紫云清夏_TameLieOneStep = Image(path=sprite_path(r"5031808b-5525-4118-92b4-317ec8bda985.png"), name="")
    
        篠泽广_光景 = Image(path=sprite_path(r"ae9fe233-9acc-4e96-ba8e-1fb1d9bc2ea5.png"), name="")
    
        倉本千奈_WonderScale = Image(path=sprite_path(r"8f8b7b46-53bb-42ab-907a-4ea87eb09ab4.png"), name="")
    
        有村麻央_Fluorite = Image(path=sprite_path(r"0d9ac648-eefa-4869-ac99-1b0c83649681.png"), name="")
    
        姬崎莉波_clumsy_trick = Image(path=sprite_path(r"921eefeb-730e-46fc-9924-d338fb286592.png"), name="")
    
    
        pass

    pass
class Produce:
    
    BoxProduceOngoing = HintBox(x1=179, y1=937, x2=551, y2=1091, source_resolution=(720, 1280))

    ButtonAutoSet = Image(path=sprite_path(r"de9a2945-a7f4-4832-afc3-05c165f45253.png"), name="button_auto_set.png")

    ButtonProduce = Image(path=sprite_path(r"f8a43bc9-2e37-447f-9b2d-190ab81dd9a3.png"), name="button_produce.png")

    ButtonProduceStart = Image(path=sprite_path(r"59e78d4c-a667-4c03-9c7e-8ca38ae87d5e.png"), name="button_produce_start.png")

    ButtonRegular = Image(path=sprite_path(r"5b4c2e1e-f7ca-4848-81e4-d72b3e1e6cbb.png"), name="button_regular.png")

    CheckboxIconNoteBoost = Image(path=sprite_path(r"cf41bd4a-c24d-4cd3-bc17-c60e08e9f4c7.png"), name="checkbox_icon_note_boost.png")

    CheckboxIconSupportPtBoost = Image(path=sprite_path(r"83b89ff8-748b-4ed4-99d7-91eed6825f04.png"), name="checkbox_icon_support_pt_boost.png")

    IconPIdolLevel = Image(path=sprite_path(r"30a6f399-6999-4f04-bb77-651e0214112f.png"), name="P偶像卡上的等级图标")

    KbIdolOverviewName = HintBox(x1=140, y1=16, x2=615, y2=97, source_resolution=(720, 1280))

    BoxIdolOverviewIdols = HintBox(x1=26, y1=568, x2=696, y2=992, source_resolution=(720, 1280))

    ButtonResume = Image(path=sprite_path(r"ccbcb114-7f73-43d1-904a-3a7ae660c531.png"), name="再開する")

    ResumeDialogRegular = Image(path=sprite_path(r"daf3d823-b7f1-4584-acf3-90b9d880332c.png"), name="培育再开对话框 REGULAR")

    BoxResumeDialogWeeks = HintBox(x1=504, y1=559, x2=643, y2=595, source_resolution=(720, 1280))

    BoxResumeDialogIdolCard = HintBox(x1=53, y1=857, x2=197, y2=1048, source_resolution=(720, 1280))

    ResumeDialogPro = Image(path=sprite_path(r"c954e153-d3e9-4488-869f-d00cfdfac5ee.png"), name="培育再开对话框 PRO")

    ResumeDialogMaster = Image(path=sprite_path(r"3c8b477a-8eda-407e-9e9f-7540c8808f89.png"), name="培育再开对话框 MASTER")

    BoxResumeDialogWeeks_Saving = HintBox(x1=499, y1=377, x2=638, y2=413, source_resolution=(720, 1280))

    BoxResumeDialogIdolCard_Saving = HintBox(x1=54, y1=674, x2=197, y2=867, source_resolution=(720, 1280))

    RadioTextSkipCommu = Image(path=sprite_path(r"aaaf79a0-c3ca-422f-8391-818de28b06b2.png"), name="radio_text_skip_commu.png")

    TextAnotherIdolAvailableDialog = Image(path=sprite_path(r"cbf4ce9c-f8d8-4fb7-a197-15bb9847df04.png"), name="Another 版本偶像可用对话框标题")

    SwitchEventModeOff = Image(path=sprite_path(r"c5356ad6-0f1e-42be-b090-059f33ea7cee.png"), name="イベントモード 切换开关 OFF")

    SwitchEventModeOn = Image(path=sprite_path(r"44097699-487f-4932-846a-095a427f4ed8.png"), name="イベントモード 切换开关 ON")

    ScreenshotMemoryConfirmDialog = Image(path=sprite_path(r"a3a2a30d-cb78-474e-aa04-adbace86ae3a.png"), name="screenshot_memory_confirm_dialog.png")

    LogoNia = Image(path=sprite_path(r"a0bd6a5f-784d-4f0a-9d66-10f4b80c8d3e.png"), name="NIA LOGO (NEXT IDOL AUDITION)")

    PointNiaToHajime = HintPoint(x=34, y=596)

    TextAPInsufficient = Image(path=sprite_path(r"4883c564-f950-4a29-9f5f-6f924123cd22.png"), name="培育 AP 不足提示弹窗 标题")

    ButtonRefillAP = Image(path=sprite_path(r"eaba6ebe-f0df-4918-aee5-ef4e3ffedcf0.png"), name="确认恢复AP按钮")

    ButtonUse = Image(path=sprite_path(r"cfc9c8e8-cbe1-49f0-9afa-ead7f9455a2e.png"), name="按钮「使う」")

    ScreenshotNoEnoughAp3 = Image(path=sprite_path(r"2c54a6f0-a315-4290-85be-01519988e7fe.png"), name="screenshot_no_enough_ap_3.png")

    ButtonSkipLive = Image(path=sprite_path(r"e5e84f9e-28da-4cf4-bcba-c9145fe39b07.png"), name="培育结束跳过演出按钮")

    TextSkipLiveDialogTitle = Image(path=sprite_path(r"b6b94f21-ef4b-4425-9c7e-ca2b574b0add.png"), name="跳过演出确认对话框标题")

    ButtonHajime0Regular = Image(path=sprite_path(r"6cd80be8-c9b3-4ba5-bf17-3ffc9b000743.png"), name="")

    ButtonHajime0Pro = Image(path=sprite_path(r"55f7db71-0a18-4b3d-b847-57959b8d2e32.png"), name="")

    TitleIconProudce = Image(path=sprite_path(r"0bf5e34e-afc6-4447-bbac-67026ce2ad26.png"), name="培育页面左上角标题图标")

    ButtonHajime1Regular = Image(path=sprite_path(r"3b473fe6-e147-477f-b088-9b8fb042a4f6.png"), name="")

    ButtonHajime1Pro = Image(path=sprite_path(r"2ededcf5-1d80-4e2a-9c83-2a31998331ce.png"), name="")

    ButtonHajime1Master = Image(path=sprite_path(r"24e99232-9434-457f-a9a0-69dd7ecf675f.png"), name="")

    PointHajimeToNia = HintPoint(x=680, y=592)

    LogoHajime = Image(path=sprite_path(r"e6b45405-cd9f-4c6e-a9f1-6ec953747c65.png"), name="Hajime LOGO 定期公演")

    ButtonPIdolOverview = Image(path=sprite_path(r"e88c9ad1-ec37-4fcd-b086-862e1e7ce8fd.png"), name="Pアイドルー覧  P偶像列表展示")

    TextStepIndicator1 = Image(path=sprite_path(r"44ba8515-4a60-42c9-8878-b42e4e34ee15.png"), name="1. アイドル選択")

    BoxSelectedIdol = HintBox(x1=149, y1=783, x2=317, y2=1006, source_resolution=(720, 1280))

    BoxSetCountIndicator = HintBox(x1=66, y1=651, x2=139, y2=686, source_resolution=(720, 1280))

    PointProduceNextSet = HintPoint(x=702, y=832)

    PointProducePrevSet = HintPoint(x=14, y=832)

    TextStepIndicator2 = Image(path=sprite_path(r"a48324ae-7c1a-489e-b3c4-93d12267f88d.png"), name="2. サポート選択")

    EmptySupportCardSlot = Image(path=sprite_path(r"d3424d31-0502-4623-996e-f0194e5085ce.png"), name="空支援卡槽位")

    TextAutoSet = Image(path=sprite_path(r"f5c16d2f-ebc5-4617-9b96-971696af7c52.png"), name="おまかせ編成")

    TextStepIndicator3 = Image(path=sprite_path(r"f43c313b-8a7b-467b-8442-fc5bcb8b4388.png"), name="3.メモリー選択")

    TextRentAvailable = Image(path=sprite_path(r"74ec3510-583d-4a76-ac69-38480fbf1387.png"), name="レンタル可能")

    TextStepIndicator4 = Image(path=sprite_path(r"b62bf889-da3c-495a-8707-f3bde73efe92.png"), name="4.開始確認")


    pass
class InPurodyuusu:
    
    A = Image(path=sprite_path(r"29774af8-a442-4d67-ab33-5c55d6878847.png"), name="A.png")

    AcquireBtnDisabled = Image(path=sprite_path(r"b804d87f-39ef-433d-8316-b44ea2d5eb6a.png"), name="acquire_btn_disabled.png")

    ButtonCancel = Image(path=sprite_path(r"df8c55ed-0ebb-466d-b337-a7a5d8e5ee99.png"), name="button_cancel.png")

    ButtonComplete = Image(path=sprite_path(r"5049dd7e-618f-443d-9bb5-0a8412b5827d.png"), name="button_complete.png")

    ButtonFinalPracticeDance = Image(path=sprite_path(r"f70a1ee8-c32f-44a8-8351-79ffdb8bf54c.png"), name="button_final_practice_dance.png")

    ButtonFinalPracticeVisual = Image(path=sprite_path(r"53d465ef-2691-4d3f-a1bf-4f3106e83a7a.png"), name="button_final_practice_visual.png")

    ButtonFinalPracticeVocal = Image(path=sprite_path(r"fd198ca0-75d8-4da8-a809-a630df3bf17f.png"), name="button_final_practice_vocal.png")

    ButtonFollowNoIcon = Image(path=sprite_path(r"a2684732-20c2-4167-884d-64e6120df305.png"), name="button_follow_no_icon.png")

    ButtonIconStudy = Image(path=sprite_path(r"9a00a0b0-bb3d-4959-9496-4c0fe49f5b09.png"), name="button_icon_study.png")

    ButtonIconStudyVisual = Image(path=sprite_path(r"6add5b86-b5da-4f0c-a3a5-b77a29bc4425.png"), name="button_icon_study_visual.png")

    ButtonLeave = Image(path=sprite_path(r"08e6a9f3-17f0-4866-b993-6bca4b7e4778.png"), name="button_leave.png")

    ButtonNextNoIcon = Image(path=sprite_path(r"93ca85ac-8f42-44ab-b272-a0b9b1ad64b3.png"), name="button_next_no_icon.png")

    ButtonRetry = Image(path=sprite_path(r"01adbe31-36d8-4a05-8237-2fe33cefc4ed.png"), name="button_retry.png")

    ButtonTextActionOuting = Image(path=sprite_path(r"fd2618b0-bfc5-4ace-a2bc-2917d1303872.png"), name="button_text_action_outing.png")

    ButtonTextAllowance = Image(path=sprite_path(r"95550cc7-baa1-485b-a685-3cc276626065.png"), name="button_text_allowance.png")

    ButtonTextConsult = Image(path=sprite_path(r"8e8affdd-8500-4f03-b4d1-15da41202831.png"), name="button_text_consult.png")

    IconClearBlue = Image(path=sprite_path(r"3428c82e-c21b-4d41-af79-e5a74afe29b1.png"), name="icon_clear_blue.png")

    IconTitleAllowance = Image(path=sprite_path(r"fff908ef-e236-428f-b74a-dc3f9bb81781.png"), name="icon_title_allowance.png")

    IconTitleStudy = Image(path=sprite_path(r"83ee05ab-6c4f-4057-b6c5-0ef7cb4810de.png"), name="icon_title_study.png")

    LootboxSliverLock = Image(path=sprite_path(r"941fb997-4161-40d7-9bb1-938cdce3e3ab.png"), name="lootbox_sliver_lock.png")

    LootBoxSkillCard = Image(path=sprite_path(r"06da77cb-274f-464d-84bf-e39047b68ba0.png"), name="loot_box_skill_card.png")

    M = Image(path=sprite_path(r"b3e46a3f-d6b4-4725-aa6e-5fd42f410814.png"), name="M.png")

    BoxExamTop = HintBox(x1=5, y1=2, x2=712, y2=55, source_resolution=(720, 1280))

    BoxCardLetter = HintBox(x1=6, y1=1081, x2=715, y2=1100, source_resolution=(720, 1280))

    BoxDrink = HintBox(x1=39, y1=1150, x2=328, y2=1244, source_resolution=(720, 1280))

    BoxDrink1 = HintBox(x1=53, y1=1166, x2=121, y2=1234, source_resolution=(720, 1280))

    BoxDrink2 = HintBox(x1=149, y1=1166, x2=217, y2=1234, source_resolution=(720, 1280))

    BoxDrink3 = HintBox(x1=245, y1=1166, x2=313, y2=1234, source_resolution=(720, 1280))

    PDrinkIcon = Image(path=sprite_path(r"7409cb73-b89c-4324-87db-8286c4dba3cc.png"), name="p_drink_icon.png")

    PItemIconColorful = Image(path=sprite_path(r"0d516b33-3895-4f24-a11e-41325edc3d5c.png"), name="p_item_icon_colorful.png")

    PSkillCardIconBlue = Image(path=sprite_path(r"a06ab5cb-dea1-4855-b89c-5a51544f3dc8.png"), name="p_skill_card_icon_blue.png")

    PSkillCardIconColorful = Image(path=sprite_path(r"46151387-0244-4146-9fa1-da5c7d798a86.png"), name="p_skill_card_icon_colorful.png")

    Rest = Image(path=sprite_path(r"464b2aaa-5529-46a3-a3c9-de8dd172d4c8.png"), name="rest.png")

    RestConfirmBtn = Image(path=sprite_path(r"36d629e8-6d19-404e-b25a-751f3fb5922d.png"), name="rest_confirm_btn.png")

    Screenshot1Cards = Image(path=sprite_path(r"8fe5063b-17cd-4866-84b5-ff600714cdf4.png"), name="screenshot_1_cards.png")

    Screenshot4Cards = Image(path=sprite_path(r"36e28bfa-2637-4667-84db-688500698041.png"), name="screenshot_4_cards.png")

    Screenshot5Cards = Image(path=sprite_path(r"3f626359-ad15-4149-8f03-62574220e781.png"), name="screenshot_5_cards.png")

    BoxWeeksUntilExam = HintBox(x1=11, y1=8, x2=237, y2=196, source_resolution=(720, 1280))

    TextActionVocal = Image(path=sprite_path(r"d6b64759-26b7-45b1-bf8e-5c0d98611e0d.png"), name="Vo. レッスン")

    TextActionDance = Image(path=sprite_path(r"303cccc1-c674-4d3a-8c89-19ea729fdbef.png"), name="Da. レッスン")

    TextActionVisual = Image(path=sprite_path(r"cc8a495d-330d-447d-8a80-a8a6ecc409c5.png"), name="Vi. レッスン")

    IconAsariSenseiAvatar = Image(path=sprite_path(r"d7667903-7149-4f2f-9c15-d8a4b5f4d347.png"), name="Asari 老师头像")

    BoxAsariSenseiTip = HintBox(x1=245, y1=150, x2=702, y2=243, source_resolution=(720, 1280))

    ButtonPracticeVocal = Image(path=sprite_path(r"ce1d1d6f-38f2-48bf-98bd-6e091c7ca5b8.png"), name="行动页 声乐课程按钮图标")

    ButtonPracticeDance = Image(path=sprite_path(r"b2e1bf3c-2c36-4fb5-9db7-c10a29563a37.png"), name="行动页 舞蹈课程按钮图标")

    ButtonPracticeVisual = Image(path=sprite_path(r"adc533a7-970b-4c5b-a037-2181531a35d6.png"), name="行动页 形象课程按钮图标")

    TextFinalExamRemaining = Image(path=sprite_path(r"70898bf8-56c5-4f84-becb-629c9ab6a7da.png"), name="最終まで")

    ButtonIconOuting = Image(path=sprite_path(r"8ded6c98-85ea-4858-a66d-4fc8caecb7c5.png"), name="行动按钮图标 外出（おでかけ）")

    ButtonIconConsult = Image(path=sprite_path(r"d83f338d-dde3-494b-9bea-cae511e3517c.png"), name="行动按钮图标 咨询（相談）")

    TextMidExamRemaining = Image(path=sprite_path(r"ce20a856-5629-4f8e-a8e1-d1bd14e18e4f.png"), name="中間まで")

    IconTitleConsult = Image(path=sprite_path(r"23d88465-65d9-4718-8725-8dbf0a98a5a4.png"), name="「相談」页面左上角图标")

    PointConsultFirstItem = HintPoint(x=123, y=550)

    ButtonEndConsult = Image(path=sprite_path(r"9fd0753f-c607-4d49-82d1-40bda27e014f.png"), name="相談 结束按钮")

    ButtonIconExchange = Image(path=sprite_path(r"4096cffa-a889-4622-852e-760fc7022d93.png"), name="交换按钮的图标")

    TextExchangeConfirm = Image(path=sprite_path(r"25f00ee3-8dfe-42d1-a67e-191fa5c3df4b.png"), name="交換確認")

    ScreenshotDrinkTest = Image(path=sprite_path(r"d7f74cdb-9b98-44f6-93cd-b1f0936c074a.png"), name="screenshot_drink_test.png")

    ScreenshotDrinkTest3 = Image(path=sprite_path(r"513b6380-48c1-4ddf-8783-cb346ea6250a.png"), name="screenshot_drink_test_3.png")

    TextRechallengeEndProduce = Image(path=sprite_path(r"207594fa-6a0b-45ec-aeff-b3e45348c508.png"), name="再挑战对话框的结束培育")

    TextGoalClearNext = Image(path=sprite_path(r"05890a1b-8764-4e9f-9d21-65d292c22e13.png"), name="培育目标达成 NEXT 文字")

    BoxLessonCards5_1 = HintBox(x1=16, y1=882, x2=208, y2=1136, source_resolution=(720, 1280))

    BoxNoSkillCard = HintBox(x1=180, y1=977, x2=529, y2=1026, source_resolution=(720, 1280))

    TitleIconOuting = Image(path=sprite_path(r"ee4e512b-4982-49b6-9c71-31984b58e1d0.png"), name="外出（おでかけ）页面 标题图标")

    TextPDrinkMaxConfirmTitle = Image(path=sprite_path(r"582d36c0-0916-4706-9833-4fbc026701f5.png"), name="P饮料溢出 不领取弹窗标题")

    ButtonUse = Image(path=sprite_path(r"a3736105-b3e6-467b-888a-f93b8f4d37be.png"), name="使用按钮（使用饮料按钮）")

    IconTitleSkillCardRemoval = Image(path=sprite_path(r"bab6c393-692c-4681-ac0d-76c0d9dabea6.png"), name="技能卡自选删除 标题图标")

    ButtonRemove = Image(path=sprite_path(r"00551158-fee9-483f-b034-549139a96f58.png"), name="削除")

    TextPDrink = Image(path=sprite_path(r"8c179a21-be6f-4db8-a9b0-9afeb5c36b1c.png"), name="文本「Pドリンク」")

    TextDontClaim = Image(path=sprite_path(r"e4683def-8d1d-472b-a5ab-bb3885c0c98e.png"), name="受け取らない")

    ButtonDontClaim = Image(path=sprite_path(r"447d0e44-5d87-4b7c-8e60-edb111fe1639.png"), name="「受け取らない」按钮")

    BoxSelectPStuffComfirm = HintBox(x1=256, y1=1064, x2=478, y2=1128, source_resolution=(720, 1280))

    TextClaim = Image(path=sprite_path(r"c948f136-416f-447e-8152-54a1cd1d1329.png"), name="文字「受け取る」")

    TextPItem = Image(path=sprite_path(r"0c0627be-4a09-4450-a078-1858d3ace532.png"), name="文字「Pアイテム」")

    TextSkillCard = Image(path=sprite_path(r"d271a24f-efe8-424d-8fd5-f6b3756ba4ca.png"), name="文字「スキルカード」")

    TextRecommend = Image(path=sprite_path(r"b0283997-7931-476d-a92f-d7569f6ea34c.png"), name="おすすめ")

    ScreenshotSenseiTipConsult = Image(path=sprite_path(r"f1c75d8d-a5b4-4883-a56a-b3c8019c8463.png"), name="screenshot_sensei_tip_consult.png")

    TextSkillCardSelectGuideDialogTitle = Image(path=sprite_path(r"3f637e86-6b74-4693-9131-1fe411fc21e5.png"), name="獲得ガイド表示設定")

    BoxSkillCardAcquired = HintBox(x1=194, y1=712, x2=528, y2=765, source_resolution=(720, 1280))

    IconSkillCardEventBubble = Image(path=sprite_path(r"6b58d90d-2e5e-4b7f-bc01-941f2633de89.png"), name="技能卡事件气泡框图标")

    ScreenshotSkillCardEnhanceDialog = Image(path=sprite_path(r"b9a8288f-bff6-4c74-b0c0-3090fe9558e8.png"), name="screenshot_skill_card_enhance_dialog.png")

    IconTitleSkillCardEnhance = Image(path=sprite_path(r"79abd239-5eed-4195-9fa8-d729daa874ca.png"), name="技能卡强化 标题 图标")

    ButtonEnhance = Image(path=sprite_path(r"da439e8c-3b74-4371-9657-0736d826c7d1.png"), name="技能卡 强化按钮")

    IconTitleSkillCardMove = Image(path=sprite_path(r"db7d3f03-1f7f-43bf-8125-f7c2d345fca2.png"), name="培育中技能卡移动对话框")

    BoxSkillCardMoveButtonCount = HintBox(x1=339, y1=1170, x2=381, y2=1195, source_resolution=(720, 1280))

    T = Image(path=sprite_path(r"16fbc93d-b294-4001-b4e9-ee2af181415f.png"), name="睡意卡字母 T（眠気）")

    IconSp = Image(path=sprite_path(r"d982d2b5-4bc0-4ae9-a516-f29c2848d64b.png"), name="SP 课程图标")

    BoxCommuEventButtonsArea = HintBox(x1=14, y1=412, x2=703, y2=1089, source_resolution=(720, 1280))

    TextSelfStudyVocal = Image(path=sprite_path(r"c78c38cc-7b61-4dc4-820d-0a5b684ef52e.png"), name="文化课事件 自习 声乐")

    TextSelfStudyDance = Image(path=sprite_path(r"83d0a033-466c-463a-bb8c-be0f2953e9b2.png"), name="文化课事件 自习 舞蹈")

    TextSelfStudyVisual = Image(path=sprite_path(r"4695f96b-c4f5-4bb6-a021-a13b6ceb2883.png"), name="文化课事件 自习 形象")

    TextAsariProduceEnd = Image(path=sprite_path(r"43ad4667-2bc6-4810-b433-0a19759ce11e.png"), name="text_asari_produce_end.png")

    TextButtonExamSkipTurn = Image(path=sprite_path(r"b133393d-2d68-45fd-bb31-913620c958c7.png"), name="text_button_exam_skip_turn.png")

    TextClearUntil = Image(path=sprite_path(r"dd067648-8a04-4aa9-9a16-24c9de418e88.png"), name="text_clear_until.png")

    TextDance = Image(path=sprite_path(r"5b8d350c-43a6-494a-8d03-1ee2bb212ccf.png"), name="text_dance.png")

    TextFinalProduceRating = Image(path=sprite_path(r"eae96173-ff42-4017-9c39-51ad7c927d6e.png"), name="text_final_produce_rating.png")

    TextOneWeekRemaining = Image(path=sprite_path(r"d5fbc984-e4c6-4764-9113-78db31719322.png"), name="text_one_week_remaining.png")

    TextPerfectUntil = Image(path=sprite_path(r"4cdd751c-5215-4450-98e3-634172a38fdb.png"), name="text_perfect_until.png")

    TextPleaseSelectPDrink = Image(path=sprite_path(r"448a2910-0302-403b-9c34-5ed0df22e6a3.png"), name="text_please_select_p_drink.png")

    TextPDiary = Image(path=sprite_path(r"731825eb-1cf2-46a1-9940-68e71fa3df81.png"), name="text_p_diary.png")

    TextPDrinkMax = Image(path=sprite_path(r"c1e3bee2-182c-48ed-9c70-ed1df0d119f9.png"), name="text_p_drink_max.png")

    TextSenseiTipConsult = Image(path=sprite_path(r"41e03f7a-b804-48f9-9f91-6ab4bfffbb60.png"), name="text_sensei_tip_consult.png")

    TextSenseiTipDance = Image(path=sprite_path(r"0e574856-8035-43db-9c7d-2634ad1abe11.png"), name="text_sensei_tip_dance.png")

    TextSenseiTipRest = Image(path=sprite_path(r"39e6af00-ad55-44b0-bbe1-1c414bf3fe33.png"), name="text_sensei_tip_rest.png")

    TextSenseiTipVisual = Image(path=sprite_path(r"f375180c-adb0-4d88-b6d7-85a067c17479.png"), name="text_sensei_tip_visual.png")

    TextSenseiTipVocal = Image(path=sprite_path(r"6421c6af-31cb-4059-8e89-ebce1e51026e.png"), name="text_sensei_tip_vocal.png")

    TextSkipTurnDialog = Image(path=sprite_path(r"4679d64d-6e85-4ed5-944c-adcfbce974a2.png"), name="text_skip_turn_dialog.png")

    TextVisual = Image(path=sprite_path(r"9998b2b8-0e61-4f08-927b-0818473dbd43.png"), name="text_visual.png")


    pass
class Kuyo:
    
    ButtonStartGame = Image(path=sprite_path(r"67270259-86f0-4b0b-9907-9705de2ac309.png"), name="button_start_game.png")

    ButtonTab3Speedup = Image(path=sprite_path(r"e2363607-467a-43a0-9551-559692bce748.png"), name="button_tab3_speedup.png")


    pass