import pefile

pe = pefile.PE("D:\\10_git\\gtec-ble-dev\\src\\gtec_ble\\lib\\native\\windows\\x64\\libgtecble.dll")
for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
    print(hex(pe.OPTIONAL_HEADER.ImageBase + exp.address), exp.name)