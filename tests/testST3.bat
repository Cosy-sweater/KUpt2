cd ./src
py app.py --package=Test.Core --path=../test-package/PackageA.txt -T --filter="STH"
py app.py --package=Google.Protobuf --path=https://www.nuget.org/packages/Google.Protobuf --filter="System"
py app.py --package=Google.Protobuf --path=https://www.nuget.org/packages/Google.Protobuf