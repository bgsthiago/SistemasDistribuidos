import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.nio.channels.FileChannel;
import java.io.IOException;
import java.nio.file.Path;


public class FileManager implements FileManagerInterface {
    Path dirPath;

    public FileManager(Path dirPath) {
        this.dirPath = dirPath;
    }

    public Boolean uploadFile(byte[] stream, String filename, int size) {

        Path filePath = this.dirPath.resolve(filename);
        File file = new File(filePath.toString());

        // avoid duplicate files
        if (file.exists()) {
            return false;
        }
        
        try {
            FileOutputStream out = new FileOutputStream(file);
            byte[] data = stream;
            out.write(data);
            out.flush();
            out.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return true;
    }
}