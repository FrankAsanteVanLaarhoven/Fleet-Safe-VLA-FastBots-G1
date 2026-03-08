use framework "AppKit"
on run argv
    set imagePath to item 1 of argv
    set targetPath to item 2 of argv
    set img to current application's NSImage's alloc()'s initWithContentsOfFile:imagePath
    set sharedWS to current application's NSWorkspace's sharedWorkspace()
    sharedWS's setIcon:img forFile:targetPath options:0
end run
