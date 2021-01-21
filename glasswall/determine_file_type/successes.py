

from glasswall.determine_file_type.classes import FileTypeEnumSuccess


# The file types that we support.
class ft_pdf(FileTypeEnumSuccess):
    integer = 16
    string = "pdf"


class ft_doc(FileTypeEnumSuccess):
    integer = 17
    string = "doc"


class ft_docx(FileTypeEnumSuccess):
    integer = 18
    string = "docx"


class ft_ppt(FileTypeEnumSuccess):
    integer = 19
    string = "ppt"


class ft_pptx(FileTypeEnumSuccess):
    integer = 20
    string = "pptx"


class ft_xls(FileTypeEnumSuccess):
    integer = 21
    string = "xls"


class ft_xlsx(FileTypeEnumSuccess):
    integer = 22
    string = "xlsx"


class ft_png(FileTypeEnumSuccess):
    integer = 23
    string = "png"


class ft_jpeg(FileTypeEnumSuccess):
    integer = 24
    string = "jpeg"


class ft_gif(FileTypeEnumSuccess):
    integer = 25
    string = "gif"


class ft_emf(FileTypeEnumSuccess):
    integer = 26
    string = "emf"


class ft_wmf(FileTypeEnumSuccess):
    integer = 27
    string = "wmf"


class ft_rtf(FileTypeEnumSuccess):
    integer = 28
    string = "rtf"


class ft_bmp(FileTypeEnumSuccess):
    integer = 29
    string = "bmp"


class ft_tiff(FileTypeEnumSuccess):
    integer = 30
    string = "tiff"


class ft_pe(FileTypeEnumSuccess):
    integer = 31
    string = "pe"


class ft_macho(FileTypeEnumSuccess):
    integer = 32
    string = "macho"


class ft_elf(FileTypeEnumSuccess):
    integer = 33
    string = "elf"


class ft_mp4(FileTypeEnumSuccess):
    integer = 34
    string = "mp4"


class ft_mp3(FileTypeEnumSuccess):
    integer = 35
    string = "mp3"


class ft_mp2(FileTypeEnumSuccess):
    integer = 36
    string = "mp2"


class ft_wav(FileTypeEnumSuccess):
    integer = 37
    string = "wav"


class ft_mpg(FileTypeEnumSuccess):
    integer = 38
    string = "mpg"


class ft_coff(FileTypeEnumSuccess):
    integer = 39
    string = "coff"


class ft_json(FileTypeEnumSuccess):
    integer = 40
    string = "json"


# Supported by an external library.
class ft_zip(FileTypeEnumSuccess):
    integer = 256
    string = "zip"


class ft_gzip(FileTypeEnumSuccess):
    integer = 257
    string = "gzip"


class ft_bzip2(FileTypeEnumSuccess):
    integer = 258
    string = "bzip2"


class ft_7zip(FileTypeEnumSuccess):
    integer = 259
    string = "7zip"


class ft_rar(FileTypeEnumSuccess):
    integer = 260
    string = "rar"


class ft_tar(FileTypeEnumSuccess):
    integer = 261
    string = "tar"


# Required since they can be embedded within other files.
class ft_ooxml(FileTypeEnumSuccess):
    integer = 512
    string = "ooxml"


class ft_office(FileTypeEnumSuccess):
    integer = 513
    string = "office"


class ft_bin(FileTypeEnumSuccess):
    integer = 514
    string = "bin"


class ft_xml(FileTypeEnumSuccess):
    integer = 515
    string = "xml"


# Required for OOXML files wrapped in CFB packages.
class ft_docxPackageInCfb(FileTypeEnumSuccess):
    integer = 768
    string = "docxPackageInCfb"


class ft_xlsxPackageInCfb(FileTypeEnumSuccess):
    integer = 769
    string = "xlsxPackageInCfb"


class ft_pptxPackageInCfb(FileTypeEnumSuccess):
    integer = 770
    string = "pptxPackageInCfb"


# ExcelCoreStreams - our internal construct.
class ft_xlscore(FileTypeEnumSuccess):
    integer = 771
    string = "xlscore"


# WordCoreStreams - our internal construct.
class ft_doccore(FileTypeEnumSuccess):
    integer = 772
    string = "doccore"


# PowerPointCoreStreams - our internal construct.
class ft_pptcore(FileTypeEnumSuccess):
    integer = 773
    string = "pptcore"


# PowerPoint Picture Streams - our internal construct.
class ft_picturestream(FileTypeEnumSuccess):
    integer = 774
    string = "picturestream"


class ft_printersettings(FileTypeEnumSuccess):
    integer = 775
    string = "printersettings"


class ft_equationnative(FileTypeEnumSuccess):
    integer = 776
    string = "equationnative"


class ft_compobj(FileTypeEnumSuccess):
    integer = 777
    string = "compobj"


class ft_docsummary(FileTypeEnumSuccess):
    integer = 778
    string = "docsummary"


# Part of Structured File support. These are underlying mechanisms.
class ft_opc(FileTypeEnumSuccess):
    integer = 779
    string = "opc"


class ft_cfb(FileTypeEnumSuccess):
    integer = 780
    string = "cfb"


# The package used to store exported content in Glasswall.
class ft_interchangePackage(FileTypeEnumSuccess):
    integer = 781
    string = "interchangePackage"


# Required for "hybrid" PDF camera where a wrapper / dummy is required for calls to classic camera before Core2 camera.
class ft_pdf_core2(FileTypeEnumSuccess):
    integer = 782
    string = "pdf_core2"


class ft_fi(FileTypeEnumSuccess):
    integer = 783
    string = "fi"
