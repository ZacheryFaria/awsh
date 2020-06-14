If ($args[0] -eq '--configure') {
    awshpy $args
    exit
}

if ($args[0] -eq '--ls') {
    awshpy $args
    exit
}

$result = (awshpy $args) | Out-String

If (-NOT ($lastExitCode -eq 2)) {
    echo $result
    exit
}

$ip = $result.split('~')[0]
$key = $result.split('~')[1].TrimEnd("`r?`n")

ssh -o "StrictHostKeyChecking no" -i $key ubuntu@$ip
