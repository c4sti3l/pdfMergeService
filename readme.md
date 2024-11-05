# PDFMerge docker service


```
podman build -t pdf-merge-service .
```

```
docker build -t pdf-merge-service .
```
```
docker run -v /pfad/zum/lokalen/eingabe_verzeichnis:/app/input -v /pfad/zum/lokalen/ausgabe_verzeichnis:/app/output -d pdf-merge-service
```

```
podman run -v C:/PDF/input:/app/input -v C:/PDF/output:/app/output -v C:/PDF/input_single:/app/input_single -d pdf-merge-service
```

```
podman stop pdf-merge-service;
podman rm pdf-merge-service;
podman build -t pdf-merge-service;
podman run -v C:/PDF/input:/app/input -v C:/PDF/output:/app/output -v C:/PDF/input_single:/app/input_single --name pdf-merge-service -d pdf-merge-service

```
