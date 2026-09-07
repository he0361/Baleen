Add-Type -AssemblyName System.Drawing
$env:PYTHONPATH = Split-Path $PSScriptRoot -Parent
$env:PYTHONIOENCODING = 'utf-8'
$json = & "$PSScriptRoot\.venv\Scripts\python.exe" -P -c 'import json; from rich.console import Console; from Baleen.branding import make_banner; t=make_banner(); c=Console(color_system="truecolor"); print(json.dumps([{ "char":ch,"bg":t.get_style_at_offset(c,i).bgcolor.get_truecolor().hex,"fg": (t.get_style_at_offset(c,i).color.get_truecolor().hex if t.get_style_at_offset(c,i).color else "#eef6ff")} for i,ch in enumerate(t.plain)]))'
$cells = $json | ConvertFrom-Json
$bitmap = [Drawing.Bitmap]::new(1000,330)
$canvas = [Drawing.Graphics]::FromImage($bitmap)
$canvas.Clear([Drawing.ColorTranslator]::FromHtml('#121212'))
$font = [Drawing.Font]::new('Consolas',12,[Drawing.FontStyle]::Regular,[Drawing.GraphicsUnit]::Pixel)
$x=0
$y=0
foreach($cell in $cells) {
    if($cell.char -eq "`n") { $x=0; $y++; continue }
    $brush=[Drawing.SolidBrush]::new([Drawing.ColorTranslator]::FromHtml($cell.bg))
    $canvas.FillRectangle($brush,40+$x*10,45+$y*20,10,20)
    $brush.Dispose()
    if($cell.char -eq [string][char]0x2580) {
        $brush=[Drawing.SolidBrush]::new([Drawing.ColorTranslator]::FromHtml($cell.fg))
        $canvas.FillRectangle($brush,40+$x*10,45+$y*20,10,10)
        $brush.Dispose()
    } elseif($cell.char -ne ' ') {
        $brush=[Drawing.SolidBrush]::new([Drawing.ColorTranslator]::FromHtml($cell.fg))
        $canvas.DrawString($cell.char,$font,$brush,40+$x*10,45+$y*20)
        $brush.Dispose()
    }
    $x++
}
$bitmap.Save((Join-Path $PSScriptRoot 'Baleen-banner-preview.png'),[Drawing.Imaging.ImageFormat]::Png)
$font.Dispose()
$canvas.Dispose()
$bitmap.Dispose()
