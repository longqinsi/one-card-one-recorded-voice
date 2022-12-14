# Anki插件：卡片专属录音(Anki Addon - Card's Own Voice)
Anki有录音功能，在学习一张卡片时，如果你按下Shift+V，就可以开始录音，录音结束后你的录音会被自动回放一次，然后再按下V可以重复回放。这个功能可以用于跟读练习。但Anki的录音只有一份，如果你录了两次音，前面一次的就丢掉了，而且程序退出后再重新打开，上次录的音也已经被删除了。本插件是把每张卡片的录音单独保存，这样你下次来到某张卡片时，还可以重复收听自己上次在这张卡片录的音，做一个对比。

Anki can record your voice so that you can do shadow exercise, but it keeps only one record of your voice, if you have recorded more than once, the previous ones no longer exist. Additionally, the recorded voice is deleted when you exit Anki. So next time when you open Anki, you can't play you own voice you have recorded before. This Addon saves an individual voice for each card and doesn't delete it when Anki exit. So you can replay your voice for a card at any time you review this card again unless you record a new voice for the same card again.

如果一张卡片被删除了，那么它对应的录音也应被清除，由于技术原因，本插件无法做到自动跟踪卡片的删除，所以提供了一个"清理不再使用的录音文件"的菜单项。在主界面的菜单里选择：工具->清理不再使用的录音文件，如果存在需要清理的录音文件，会提示你"一共有xxx个不再使用的录音文件，请问是否清理？"，如果选择"是",将会为你清理这些文件。

Once a card is deleted, the corresponding voice should also be deleted, but due to technical limits, this addon can't track the removal of cards, so there is a menu item "Clear Unused Recorded Voices" for you to clear these unused voices. In the top menu of the main frame of the program, select Tools -> Clear Unused Recorded Voices, if there are really such voices, a dialog such as "There are xxx unused recorded voices, would you like to clear them?" will pop up, and if you press "Yes", the redundant voices will be cleared out for you.

如果你的磁盘空间实在不够用了，或者你不想保留以前的录音，当然你也可以删除全部录音。在主界面的菜单里选择：工具->删除全部录音文件，这时还是会弹出一个提示框，提醒你删除操作是不可恢复的，如果你仍然决定要删除，点击"是"即可。

If your disk space is going to be exhausted, or you don't want to keep your previous recorded voices, you can simply clear them out, but you must know what you are doing! This operation is unrecoverable! In the top menu of the main frame, select Tools -> Delete All Recorded Voices, and then select 'Yes' in the popped dialog, then all recorded voices will disappear!